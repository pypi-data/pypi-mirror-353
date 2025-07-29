/*
 * python_bindings.cpp
 *
 * Python bindings for bincraft2json using pybind11
 *
 * Author: @aymene69
 * License: MIT
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "bincraft2json.hpp"
#include <stdexcept>
#include <vector>
#include <string>

namespace py = pybind11;

/**
 * Decode a BinCraft file and return a JSON string
 */
std::string decode_bincraft_file(const std::string& filename, bool zstd_compressed) {
    try {
        nlohmann::json result = decodeBinCraftToJson(filename, zstd_compressed);
        return result.dump();
    } catch (const std::exception& e) {
        throw std::runtime_error("Error decoding file: " + std::string(e.what()));
    }
}

/**
 * Decode BinCraft binary data in memory and return a JSON string
 */
std::string decode_bincraft_bytes(const py::bytes& data, bool zstd_compressed) {
    try {
        // Convert py::bytes to std::vector<uint8_t>
        std::string data_str = data;
        std::vector<uint8_t> raw_data(data_str.begin(), data_str.end());
        
        std::vector<uint8_t> data_buffer;
        
        if (zstd_compressed) {
            // ZSTD decompression
            size_t decompressed_size_hint = ZSTD_getFrameContentSize(raw_data.data(), raw_data.size());
            if (decompressed_size_hint == ZSTD_CONTENTSIZE_ERROR) {
                throw std::runtime_error("Corrupted or invalid ZSTD file.");
            }
            if (decompressed_size_hint == ZSTD_CONTENTSIZE_UNKNOWN) {
                decompressed_size_hint = raw_data.size() * 3;
            }
            data_buffer.resize(decompressed_size_hint);
            size_t result = ZSTD_decompress(data_buffer.data(), data_buffer.size(), raw_data.data(), raw_data.size());
            if (ZSTD_isError(result)) {
                throw std::runtime_error("ZSTD decompression error: " + std::string(ZSTD_getErrorName(result)));
            }
            data_buffer.resize(result);
        } else {
            data_buffer = raw_data;
        }
        
        // Check if we have enough data
        if (data_buffer.size() < 20) {
            throw std::runtime_error("Insufficient binary data for header (less than 20 bytes).");
        }
        
        // Read stride from header
        uint32_t stride = read_uint32_le(data_buffer, 8);
        if (stride == 0 || data_buffer.size() < stride) {
            return "[]"; // Return empty JSON array
        }
        
        std::vector<Aircraft> aircraft_list;
        
        // Decode each aircraft
        for (size_t off = stride; off + stride <= data_buffer.size(); off += stride) {
            Aircraft ac;
            
            // Decode hex
            ac.hex = [&]() {
                uint32_t raw_hex = read_int32_le(data_buffer, off) & ((1 << 24) - 1);
                std::stringstream ss;
                ss << std::hex << std::setw(6) << std::setfill('0') << raw_hex;
                return ss.str();
            }();
            
            // Decode all other fields (copied from original function)
            ac.seen_pos = static_cast<double>(read_uint16_le(data_buffer, off + 4)) / 10.0;
            ac.seen = static_cast<double>(read_uint16_le(data_buffer, off + 6)) / 10.0;
            ac.lat = static_cast<double>(read_int32_le(data_buffer, off + 8)) / 1e6;
            ac.lon = static_cast<double>(read_int32_le(data_buffer, off + 12)) / 1e6;
            ac.alt_baro = static_cast<int32_t>(read_int16_le(data_buffer, off + 16)) * 25;
            ac.alt_geom = static_cast<int32_t>(read_int16_le(data_buffer, off + 18)) * 25;
            ac.baro_rate = read_int16_le(data_buffer, off + 20) * 8;
            ac.geom_rate = read_int16_le(data_buffer, off + 22) * 8;
            ac.nav_altitude_mcp = read_uint16_le(data_buffer, off + 24) * 4;
            ac.nav_altitude_fms = read_uint16_le(data_buffer, off + 26) * 4;
            ac.nav_qnh = static_cast<double>(read_int16_le(data_buffer, off + 28)) / 10.0;
            ac.nav_heading = static_cast<double>(read_int16_le(data_buffer, off + 30)) / 90.0;
            
            // Squawk
            ac.squawk = [&]() {
                uint16_t raw_squawk = read_uint16_le(data_buffer, off + 32);
                std::stringstream ss;
                ss << std::setw(4) << std::setfill('0') << raw_squawk;
                return ss.str();
            }();
            
            ac.gs = static_cast<double>(read_int16_le(data_buffer, off + 34)) / 10.0;
            ac.mach = static_cast<double>(read_int16_le(data_buffer, off + 36)) / 1000.0;
            ac.roll = static_cast<double>(read_int16_le(data_buffer, off + 38)) / 100.0;
            ac.track = static_cast<double>(read_int16_le(data_buffer, off + 40)) / 90.0;
            ac.track_rate = static_cast<double>(read_int16_le(data_buffer, off + 42)) / 100.0;
            ac.mag_heading = static_cast<double>(read_int16_le(data_buffer, off + 44)) / 90.0;
            ac.true_heading = static_cast<double>(read_int16_le(data_buffer, off + 46)) / 90.0;
            ac.wd = read_int16_le(data_buffer, off + 48);
            ac.ws = read_int16_le(data_buffer, off + 50);
            ac.oat = read_int16_le(data_buffer, off + 52);
            ac.tat = read_int16_le(data_buffer, off + 54);
            ac.tas = read_uint16_le(data_buffer, off + 56);
            ac.ias = read_uint16_le(data_buffer, off + 58);
            ac.rc = read_uint16_le(data_buffer, off + 60);
            ac.messages = read_uint16_le(data_buffer, off + 62);
            
            // Category
            uint8_t raw_category = read_uint8(data_buffer, off + 64);
            if (raw_category) {
                std::stringstream ss;
                ss << std::hex << std::uppercase << static_cast<int>(raw_category);
                ac.category = ss.str();
            } else {
                ac.category = "";
            }
            
            ac.nic = read_uint8(data_buffer, off + 65);
            
            // Byte 67
            uint8_t byte67 = read_uint8(data_buffer, off + 67);
            ac.emergency = byte67 & 0x0F;
            ac.type = getType((byte67 & 0xF0) >> 4);
            
            // Byte 68
            uint8_t byte68 = read_uint8(data_buffer, off + 68);
            ac.airground = byte68 & 0x0F;
            ac.nav_altitude_src = (byte68 & 0xF0) >> 4;
            
            // Bytes 69-73
            uint8_t byte69 = read_uint8(data_buffer, off + 69);
            ac.sil_type = byte69 & 0x0F;
            ac.adsb_version = (byte69 & 0xF0) >> 4;
            
            uint8_t byte70 = read_uint8(data_buffer, off + 70);
            ac.adsr_version = byte70 & 0x0F;
            ac.tisb_version = (byte70 & 0xF0) >> 4;
            
            uint8_t byte71 = read_uint8(data_buffer, off + 71);
            ac.nac_p = byte71 & 0x0F;
            ac.nac_v = (byte71 & 0xF0) >> 4;
            
            uint8_t byte72 = read_uint8(data_buffer, off + 72);
            ac.sil = byte72 & 0x03;
            ac.gva = (byte72 & 0x0C) >> 2;
            ac.sda = (byte72 & 0x30) >> 4;
            ac.nic_a = (byte72 & 0x40) >> 6;
            ac.nic_c = (byte72 & 0x80) >> 7;
            
            // RSSI
            uint8_t raw_rssi_byte = read_uint8(data_buffer, off + 86);
            ac.rssi = 10.0 * std::log10(static_cast<double>(raw_rssi_byte * raw_rssi_byte) / 65025.0 + 1.125e-5);
            
            ac.dbFlags = read_uint8(data_buffer, off + 87);
            
            // Strings
            ac.flight = genStr(data_buffer, off + 78, off + 87);
            ac.t = genStr(data_buffer, off + 88, off + 92);
            ac.r = genStr(data_buffer, off + 92, off + 104);
            ac.receiverCount = read_uint8(data_buffer, off + 104);
            
            // Byte 73
            uint8_t byte73 = read_uint8(data_buffer, off + 73);
            ac.nic_baro = (byte73 & 0x01);
            ac.alert = (byte73 & 0x02) >> 1;
            ac.spi = (byte73 & 0x04) >> 2;
            
            // Nav modes
            uint8_t nav_modes_byte = read_uint8(data_buffer, off + 66);
            if (nav_modes_byte & 0x01) ac.nav_modes.push_back("autopilot");
            if (nav_modes_byte & 0x02) ac.nav_modes.push_back("vnav");
            if (nav_modes_byte & 0x04) ac.nav_modes.push_back("alt_hold");
            if (nav_modes_byte & 0x08) ac.nav_modes.push_back("approach");
            if (nav_modes_byte & 0x10) ac.nav_modes.push_back("lnav");
            if (nav_modes_byte & 0x20) ac.nav_modes.push_back("tcas");
            
            aircraft_list.push_back(ac);
        }
        
        // Convert to JSON
        nlohmann::json j_array = nlohmann::json::array();
        for (const auto& ac : aircraft_list) {
            j_array.push_back(aircraftToJson(ac));
        }
        
        return j_array.dump();
        
    } catch (const std::exception& e) {
        throw std::runtime_error("Error decoding data: " + std::string(e.what()));
    }
}

PYBIND11_MODULE(_core, m) {
    m.doc() = "BinCraft decoding module for Python";
    
    m.def("decode_bincraft_file", &decode_bincraft_file, 
          "Decode a BinCraft file to JSON",
          py::arg("filename"), py::arg("zstd_compressed") = false);
    
    m.def("decode_bincraft_bytes", &decode_bincraft_bytes, 
          "Decode BinCraft binary data to JSON",
          py::arg("data"), py::arg("zstd_compressed") = false);
} 