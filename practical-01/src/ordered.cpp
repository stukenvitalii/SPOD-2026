#include "common.hpp"
#include <vector>

int main(int argc, char** argv) {
    MPI_Init(&argc, &argv);
    int rank = 0;
    int size = 0;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    const auto options = read_options(argc, argv, rank);
    if (show_help(options, rank)) return 0;
    std::vector<int> message(options.count, rank);

    double start = 0.0;
    if (options.benchmark) {
        MPI_Barrier(MPI_COMM_WORLD);
        start = MPI_Wtime();
    }

    for (int round = 0; round < options.rounds; ++round) {
        if (rank == 0) {
            if (!options.benchmark) print_rank(0);
            for (int source = 1; source < size; ++source) {
                MPI_Recv(message.data(), options.count, MPI_INT, source,
                         round, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
                if (!options.benchmark) print_rank(message[0]);
            }
        } else {
            MPI_Send(message.data(), options.count, MPI_INT, 0, round, MPI_COMM_WORLD);
        }
    }

    finish(options, rank, size, start, "ordered");
    return 0;
}
