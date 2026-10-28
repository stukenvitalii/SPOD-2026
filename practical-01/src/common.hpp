#pragma once

#include <mpi.h>
#include <charconv>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>

struct Options {
    int rounds = 1;
    int count = 1;
    bool benchmark = false;
    bool help = false;
};

inline int positive_int(std::string_view value) {
    int result = 0;
    auto [end, error] = std::from_chars(value.data(), value.data() + value.size(), result);
    if (error != std::errc{} || end != value.data() + value.size() || result < 1) {
        throw std::invalid_argument("Expected a positive integer: " + std::string(value));
    }
    return result;
}

inline Options read_options(int argc, char** argv, int rank) {
    Options options;
    try {
        for (int i = 1; i < argc; ++i) {
            std::string_view arg = argv[i];
            if (arg == "--benchmark") {
                options.benchmark = true;
            } else if (arg == "--help") {
                options.help = true;
            } else if (arg == "--rounds" || arg == "--count") {
                if (++i == argc) {
                    throw std::invalid_argument("Missing value for " + std::string(arg));
                }
                int value = positive_int(argv[i]);
                if (arg == "--rounds") options.rounds = value;
                else options.count = value;
            } else {
                throw std::invalid_argument("Unknown argument: " + std::string(arg));
            }
        }
        int* tag_limit = nullptr;
        int found = 0;
        MPI_Comm_get_attr(MPI_COMM_WORLD, MPI_TAG_UB, &tag_limit, &found);
        if (!found || options.rounds - 1 > *tag_limit) {
            throw std::invalid_argument("Too many rounds for this MPI implementation");
        }
    } catch (const std::exception& error) {
        if (rank == 0) std::cerr << error.what() << '\n';
        MPI_Abort(MPI_COMM_WORLD, 1);
    }
    return options;
}

inline bool show_help(const Options& options, int rank) {
    if (!options.help) return false;
    if (rank == 0) {
        std::cout << "Options: --rounds N --count N --benchmark --help\n"
                  << "count: number of MPI_INT elements per message\n"
                  << "benchmark: suppress greetings and print a CSV timing row\n";
    }
    MPI_Finalize();
    return true;
}

inline void print_rank(int rank) {
    std::cout << "Hello from " << rank << std::endl;
}

inline void finish(const Options& options, int rank, int size,
                   double start, const char* mode) {
    if (options.benchmark) {
        double elapsed = MPI_Wtime() - start;
        double maximum = 0.0;
        MPI_Reduce(&elapsed, &maximum, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);
        if (rank == 0) {
            std::cout << mode << ',' << size << ',' << options.count << ','
                      << options.rounds << ',' << std::setprecision(12)
                      << maximum << ',' << maximum / options.rounds << '\n';
        }
    }
    MPI_Finalize();
}
