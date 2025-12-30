#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "chudnovsky_calculator.h"

namespace py = pybind11;

PYBIND11_MODULE(pi_core, m) {
    m.doc() = "Pi Archiver Core - высокопроизводительные вычисления π";
    
    py::class_<pi_archiver::ChudnovskyCalculator>(m, "ChudnovskyCalculator")
        .def(py::init<int>(), py::arg("precision"))
        .def("compute_pi", &pi_archiver::ChudnovskyCalculator::compute_pi, 
             py::arg("num_threads") = 0,
             "Вычислить π с указанным количеством потоков")
        .def("set_precision", &pi_archiver::ChudnovskyCalculator::set_precision,
             py::arg("precision"),
             "Установить точность вычислений")
        .def("get_precision", &pi_archiver::ChudnovskyCalculator::get_precision,
             "Получить текущую точность")
        .def_static("get_optimal_threads", 
                   &pi_archiver::ChudnovskyCalculator::get_optimal_threads,
                   "Получить оптимальное количество потоков для системы");
    
    // Утилиты
    m.def("get_system_info", []() {
        return py::dict(
            "hardware_threads"_a = std::thread::hardware_concurrency(),
            "optimal_threads"_a = pi_archiver::ChudnovskyCalculator::get_optimal_threads()
        );
    }, "Получить информацию о системе");
    
    m.attr("__version__") = "1.0.0";
}
