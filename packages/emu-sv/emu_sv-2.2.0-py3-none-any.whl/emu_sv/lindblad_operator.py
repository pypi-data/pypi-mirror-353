import torch
from emu_base import compute_noise_from_lindbladians, matmul_2x2_with_batched


dtype = torch.complex128
sigmax = torch.tensor([[0.0, 1.0], [1.0, 0.0]], dtype=dtype)
sigmay = torch.tensor([[0.0, -1.0j], [1.0j, 0.0]], dtype=dtype)
n_op = torch.tensor([[0.0, 0.0], [0.0, 1.0]], dtype=dtype)


class RydbergLindbladian:
    """
    Apply the Lindblad superoperator ℒ to a density matrix 𝜌,  ℒ(𝜌).

    This class implements
    H @𝜌- H @ 𝜌 + i ∑ₖ − 1/2 Aₖ† Aₖ 𝜌 − 1/2 𝜌 Aₖ^† Aₖ + Aₖ 𝜌 Aₖ^†,
    where A_k is a jump operator and H is the Rydberg Hamiltonian.
    The complex -𝑖, will be multiplied in the evolution.

    Only works with effective noise channels, i.e., the jump or collapse
    operators. For more information, see:
    https://pulser.readthedocs.io/en/stable/tutorials/effective_noise.html

    Attributes:
        nqubits (int): number of qubits in the system.
        omegas (torch.Tensor): amplited frequencies  Ωⱼ for each qubit, divided by 2.
        deltas (torch.Tensor): detunings 𝛿ᵢ for each qubit.
        phis (torch.Tensor): phases 𝜙ᵢ for each qubit.
        interaction_matrix (torch.Tensor): interaction_matrix (torch.Tensor): matrix Uᵢⱼ
            representing pairwise Rydberg interaction strengths between qubits.
        pulser_linblads (list[torch.Tensor]): List of 2x2 local Lindblad (jump)
            operators acting on each qubit.
        device (torch.device): device on which tensors are allocated. cpu or gpu: cuda.
        complex (bool): flag indicating whether any drive phase is nonzero
            (i.e., complex Hamiltonian terms).
        diag (torch.Tensor): precomputed diagonal interaction term for the density matrix evolution.

    Methods:
        apply_local_op_to_density_matrix(density_matrix, local_op, target_qubit):
            Applies a local operator to the density matrix from the left: L @ ρ.

        apply_density_matrix_to_local_op_T(density_matrix, local_op, target_qubit):
            Applies a daggered local operator to the density matrix from the right: ρ @ L†.

        __matmul__(density_matrix):
            Applies the full Lindbladian superoperator to the input density matrix,
            including coherent evolution and all dissipation channels.
    """

    def __init__(
        self,
        omegas: torch.Tensor,
        deltas: torch.Tensor,
        phis: torch.Tensor,
        pulser_linblads: list[torch.Tensor],
        interaction_matrix: torch.Tensor,
        device: torch.device,
    ):
        self.nqubits: int = len(omegas)
        self.omegas: torch.Tensor = omegas / 2.0
        self.deltas: torch.Tensor = deltas
        self.phis: torch.Tensor = phis
        self.interaction_matrix: torch.Tensor = interaction_matrix
        self.pulser_linblads: list[torch.Tensor] = pulser_linblads
        self.device: torch.device = device
        self.complex = self.phis.any()

        self.diag: torch.Tensor = self._create_diagonal()

    def _create_diagonal(self) -> torch.Tensor:
        """
        Return the diagonal elements of the Rydberg Hamiltonian matrix
        concerning only the interaction

            H.diag =  ∑ᵢ﹥ⱼUᵢⱼnᵢnⱼ
        """
        diag = torch.zeros(2**self.nqubits, dtype=dtype, device=self.device)

        for i in range(self.nqubits):
            diag = diag.view(2**i, 2, -1)
            i_fixed = diag[:, 1, :]
            for j in range(i + 1, self.nqubits):
                i_fixed = i_fixed.view(2**i, 2 ** (j - i - 1), 2, -1)
                # replacing i_j_fixed by i_fixed breaks the code :)
                i_j_fixed = i_fixed[:, :, 1, :]
                i_j_fixed += self.interaction_matrix[i, j]
        return diag.view(-1)

    def apply_local_op_to_density_matrix(
        self,
        density_matrix: torch.Tensor,
        local_op: torch.Tensor,
        target_qubit: int,
    ) -> torch.Tensor:
        """
        Calculate a local operator (2x2) L being multiplied by a density matrix ρ
        from the left
        Return L @ ρ
        """

        orignal_shape = density_matrix.shape
        density_matrix = density_matrix.view(2**target_qubit, 2, -1)
        if density_matrix.is_cpu:
            density_matrix = local_op @ density_matrix
        else:
            density_matrix = matmul_2x2_with_batched(local_op, density_matrix)

        return density_matrix.view(orignal_shape)

    def apply_density_matrix_to_local_op_T(
        self,
        density_matrix: torch.Tensor,
        local_op: torch.Tensor,
        target_qubit: int,
    ) -> torch.Tensor:
        """
        Calculates a density matrix ρ being multiplied by a daggered local (2x2)
          operator L† from the right,

        return:  ρ @L†
        """

        orignal_shape = density_matrix.shape
        density_matrix = density_matrix.view(2 ** (target_qubit + self.nqubits), 2, -1)
        if density_matrix.is_cpu:
            density_matrix = local_op.conj() @ density_matrix
        else:
            density_matrix = matmul_2x2_with_batched(local_op.conj(), density_matrix)

        return density_matrix.view(orignal_shape)

    def __matmul__(self, density_matrix: torch.Tensor) -> torch.Tensor:
        """Apply the i*RydbergLindbladian operator to the density matrix ρ
        in the following way:
        Define and effective Hamiltonian
        Heff = Hρ  -0.5i ∑ₖ Lₖ† Lₖ ρ
        Then, the Lindblad operator applying to ρ is giving by
         ℒ(𝜌) = Heff - Heff^†+i*∑ₖ Lₖ ρ Lₖ†
        """

        # compute -0.5i ∑ₖ Lₖ† Lₖ
        sum_lindblad_local = compute_noise_from_lindbladians(self.pulser_linblads).to(
            self.device
        )

        # apply all local terms:  Ωⱼ σₓ - δⱼ n - 0.5i (∑ₖ Lₖ† Lₖ) to each qubit
        H_den_matrix = torch.zeros_like(density_matrix, dtype=dtype, device=self.device)

        if not self.complex:
            for qubit, (omega, delta) in enumerate(zip(self.omegas, self.deltas)):
                H_q = (
                    omega * sigmax.to(device=self.device)
                    - delta * n_op.to(device=self.device)
                    + sum_lindblad_local
                )
                H_den_matrix += self.apply_local_op_to_density_matrix(
                    density_matrix, H_q, qubit
                )
        else:
            for qubit, (omega, delta, phi) in enumerate(
                zip(self.omegas, self.deltas, self.phis)
            ):
                H_q = (
                    omega
                    * (
                        (
                            torch.cos(phi) * sigmax.to(device=self.device)
                            + torch.sin(phi) * sigmay.to(device=self.device)
                        )
                    )
                    - delta * n_op.to(device=self.device)
                    + sum_lindblad_local
                )
                H_den_matrix += self.apply_local_op_to_density_matrix(
                    density_matrix, H_q, qubit
                )

        # apply the interaction terms  ∑ᵢⱼ Uᵢⱼ nᵢ nⱼ
        H_den_matrix += self.diag.view(-1, 1) * density_matrix

        # Heff - Heff^†=  [H, ρ] - 0.5i ∑ₖ Lₖ† Lₖρ - ρ 0.5i ∑ₖ Lₖ† Lₖρ
        H_den_matrix = H_den_matrix - H_den_matrix.conj().T

        # compute ∑ₖ Lₖ ρ Lₖ†, last part of the Lindblad operator
        L_den_matrix_Ldag = sum(
            self.apply_density_matrix_to_local_op_T(
                self.apply_local_op_to_density_matrix(
                    density_matrix, L.to(self.device), qubit
                ),
                L.to(self.device),
                qubit,
            )
            for qubit in range(self.nqubits)
            for L in self.pulser_linblads
        )

        return H_den_matrix + 1.0j * L_den_matrix_Ldag
