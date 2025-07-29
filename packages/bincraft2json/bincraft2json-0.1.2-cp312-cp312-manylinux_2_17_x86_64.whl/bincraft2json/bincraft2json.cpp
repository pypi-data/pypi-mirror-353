/*
 * bincraft2json.cpp
 *
 * Author: @aymene69
 * License: MIT
 * Example usage for bincraft2json.hpp
 *
 * Compile with:
 *   g++ -std=c++17 -o bincraft2json bincraft2json.cpp -lzstd
 *
 * This program decodes a BinCraft binary file and prints the aircraft data as JSON.
 */
 
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "json.hpp"
#include "bincraft2json.hpp"
#include "bincraft2json_impl.hpp"

namespace py = pybind11;

// Fonction utilitaire pour convertir nlohmann::json en dict Python
py::dict json_to_dict(const nlohmann::json& j) {
    py::dict result;
    for (auto& [key, value] : j.items()) {
        if (value.is_object()) {
            result[key.c_str()] = json_to_dict(value);
        } else if (value.is_array()) {
            py::list list;
            for (const auto& item : value) {
                if (item.is_object()) {
                    list.append(json_to_dict(item));
                } else if (item.is_number()) {
                    list.append(item.get<double>());
                } else if (item.is_string()) {
                    list.append(item.get<std::string>());
                } else if (item.is_boolean()) {
                    list.append(item.get<bool>());
                } else if (item.is_null()) {
                    list.append(py::none());
                }
            }
            result[key.c_str()] = list;
        } else if (value.is_number()) {
            result[key.c_str()] = value.get<double>();
        } else if (value.is_string()) {
            result[key.c_str()] = value.get<std::string>();
        } else if (value.is_boolean()) {
            result[key.c_str()] = value.get<bool>();
        } else if (value.is_null()) {
            result[key.c_str()] = py::none();
        }
    }
    return result;
}

PYBIND11_MODULE(_core, m) {
    m.doc() = "BinCraft to JSON converter"; // optional module docstring

    m.def("decode_bincraft", [](const std::string& filename, bool zstd_compressed) {
        try {
            nlohmann::json result = decodeBinCraftToJson(filename, zstd_compressed);
            return json_to_dict(result);
        } catch (const std::exception& e) {
            PyErr_SetString(PyExc_RuntimeError, e.what());
            throw py::error_already_set();
        } catch (...) {
            PyErr_SetString(PyExc_RuntimeError, "Une erreur inconnue s'est produite");
            throw py::error_already_set();
        }
    }, "Decode a BinCraft binary file to JSON",
        py::arg("filename"),
        py::arg("zstd_compressed") = false
    );

    m.def("decode_bincraft_buffer", [](py::bytes buffer, bool zstd_compressed) {
        try {
            std::string buffer_str = buffer.cast<std::string>();
            std::vector<uint8_t> raw_data(buffer_str.begin(), buffer_str.end());
            std::vector<uint8_t> data_buffer;
            
            if (zstd_compressed) {
                size_t decompressed_size_hint = ZSTD_getFrameContentSize(raw_data.data(), raw_data.size());
                if (decompressed_size_hint == ZSTD_CONTENTSIZE_ERROR) 
                    throw std::runtime_error("Données ZSTD corrompues ou invalides.");
                if (decompressed_size_hint == ZSTD_CONTENTSIZE_UNKNOWN) 
                    decompressed_size_hint = raw_data.size() * 3;
                data_buffer.resize(decompressed_size_hint);
                size_t result = ZSTD_decompress(data_buffer.data(), data_buffer.size(), raw_data.data(), raw_data.size());
                if (ZSTD_isError(result)) 
                    throw std::runtime_error("Erreur de décompression ZSTD: " + std::string(ZSTD_getErrorName(result)));
                data_buffer.resize(result);
            } else {
                data_buffer = raw_data;
            }

            if (data_buffer.size() < 20) 
                throw std::runtime_error("Données binaires insuffisantes pour l'en-tête (moins de 20 octets).");

            uint32_t stride = read_uint32_le(data_buffer, 8);
            if (stride == 0 || data_buffer.size() < stride) 
                return py::dict();

            std::vector<Aircraft> aircraft_list;
            for (size_t offset = 20; offset + stride <= data_buffer.size(); offset += stride) {
                Aircraft ac;
                if (decodeAircraft(data_buffer, offset, ac)) {
                    aircraft_list.push_back(ac);
                }
            }

            nlohmann::json result = nlohmann::json::array();
            for (const auto& ac : aircraft_list) {
                result.push_back(aircraftToJson(ac));
            }
            return json_to_dict(result);
        } catch (const std::exception& e) {
            PyErr_SetString(PyExc_RuntimeError, e.what());
            throw py::error_already_set();
        } catch (...) {
            PyErr_SetString(PyExc_RuntimeError, "Une erreur inconnue s'est produite");
            throw py::error_already_set();
        }
    }, "Decode a BinCraft binary buffer to JSON",
        py::arg("buffer"),
        py::arg("zstd_compressed") = false
    );
}