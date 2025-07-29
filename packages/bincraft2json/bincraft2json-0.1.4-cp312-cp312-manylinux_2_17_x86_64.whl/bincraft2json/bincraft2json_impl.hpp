/*
 * bincraft2json_impl.hpp
 *
 * Copyright (c) 2025 @aymene69
 *
 * Implémentation des fonctions de décodage BinCraft
 */

#ifndef BINCRAFT2JSON_IMPL_HPP
#define BINCRAFT2JSON_IMPL_HPP

#include "bincraft2json.hpp"
#include <iomanip>
#include <sstream>

inline bool decodeAircraft(const std::vector<uint8_t>& data, size_t offset, Aircraft& ac) {
    if (offset + 20 > data.size()) return false;

    // Convertir l'ICAO24 en hexadécimal
    uint32_t raw_hex = read_uint32_le(data, offset) & ((1 << 24) - 1);
    std::stringstream ss;
    ss << std::hex << std::setw(6) << std::setfill('0') << raw_hex;
    ac.hex = ss.str();

    ac.seen_pos = static_cast<double>(read_uint16_le(data, offset + 4)) / 10.0;
    ac.seen = static_cast<double>(read_uint16_le(data, offset + 6)) / 10.0;
    ac.lat = static_cast<double>(read_int32_le(data, offset + 8)) / 1e6;
    ac.lon = static_cast<double>(read_int32_le(data, offset + 12)) / 1e6;
    ac.alt_baro = static_cast<int32_t>(read_int16_le(data, offset + 16)) * 25;
    ac.alt_geom = static_cast<int32_t>(read_int16_le(data, offset + 18)) * 25;
    ac.baro_rate = read_int16_le(data, offset + 20) * 8;
    ac.geom_rate = read_int16_le(data, offset + 22) * 8;
    ac.nav_altitude_mcp = read_uint16_le(data, offset + 24) * 4;
    ac.nav_altitude_fms = read_uint16_le(data, offset + 26) * 4;
    ac.nav_qnh = static_cast<double>(read_int16_le(data, offset + 28)) / 10.0;
    ac.nav_heading = static_cast<double>(read_int16_le(data, offset + 30)) / 90.0;

    // Convertir le squawk en chaîne
    uint16_t raw_squawk = read_uint16_le(data, offset + 32);
    ss.str("");
    ss << std::setw(4) << std::setfill('0') << raw_squawk;
    ac.squawk = ss.str();

    ac.gs = static_cast<double>(read_int16_le(data, offset + 34)) / 10.0;
    ac.mach = static_cast<double>(read_int16_le(data, offset + 36)) / 1000.0;
    ac.roll = static_cast<double>(read_int16_le(data, offset + 38)) / 100.0;
    ac.track = static_cast<double>(read_int16_le(data, offset + 40)) / 90.0;
    ac.track_rate = static_cast<double>(read_int16_le(data, offset + 42)) / 100.0;
    ac.mag_heading = static_cast<double>(read_int16_le(data, offset + 44)) / 90.0;
    ac.true_heading = static_cast<double>(read_int16_le(data, offset + 46)) / 90.0;
    ac.wd = read_int16_le(data, offset + 48);
    ac.ws = read_int16_le(data, offset + 50);
    ac.oat = read_int16_le(data, offset + 52);
    ac.tat = read_int16_le(data, offset + 54);
    ac.tas = read_uint16_le(data, offset + 56);
    ac.ias = read_uint16_le(data, offset + 58);
    ac.rc = read_uint16_le(data, offset + 60);
    ac.messages = read_uint16_le(data, offset + 62);

    // Catégorie
    uint8_t raw_category = read_uint8(data, offset + 64);
    if (raw_category) {
        ss.str("");
        ss << std::hex << std::uppercase << static_cast<int>(raw_category);
        ac.category = ss.str();
    } else {
        ac.category = "";
    }

    ac.nic = read_uint8(data, offset + 65);

    // Type et urgence
    uint8_t byte67 = read_uint8(data, offset + 67);
    ac.emergency = byte67 & 0x0F;
    ac.type = getType((byte67 & 0xF0) >> 4);

    // Air/Ground et source d'altitude
    uint8_t byte68 = read_uint8(data, offset + 68);
    ac.airground = byte68 & 0x0F;
    ac.nav_altitude_src = (byte68 & 0xF0) >> 4;

    // SIL type et version ADSB
    uint8_t byte69 = read_uint8(data, offset + 69);
    ac.sil_type = byte69 & 0x0F;
    ac.adsb_version = (byte69 & 0xF0) >> 4;

    // Versions ADSR et TISB
    uint8_t byte70 = read_uint8(data, offset + 70);
    ac.adsr_version = byte70 & 0x0F;
    ac.tisb_version = (byte70 & 0xF0) >> 4;

    // NAC et autres paramètres
    uint8_t byte71 = read_uint8(data, offset + 71);
    ac.nac_p = byte71 & 0x0F;
    ac.nac_v = (byte71 & 0xF0) >> 4;

    uint8_t byte72 = read_uint8(data, offset + 72);
    ac.sil = byte72 & 0x03;
    ac.gva = (byte72 & 0x0C) >> 2;
    ac.sda = (byte72 & 0x30) >> 4;
    ac.nic_a = (byte72 & 0x40) >> 6;
    ac.nic_c = (byte72 & 0x80) >> 7;

    // RSSI et flags
    uint8_t raw_rssi_byte = read_uint8(data, offset + 86);
    ac.rssi = 10.0 * std::log10(static_cast<double>(raw_rssi_byte * raw_rssi_byte) / 65025.0 + 1.125e-5);
    ac.dbFlags = read_uint8(data, offset + 87);

    // Informations de vol
    ac.flight = genStr(data, offset + 78, offset + 87);
    ac.t = genStr(data, offset + 88, offset + 92);
    ac.r = genStr(data, offset + 92, offset + 104);
    ac.receiverCount = read_uint8(data, offset + 104);

    // NIC baro, alert et SPI
    uint8_t byte73 = read_uint8(data, offset + 73);
    ac.nic_baro = (byte73 & 0x01);
    ac.alert = (byte73 & 0x02) >> 1;
    ac.spi = (byte73 & 0x04) >> 2;

    // Modes de navigation
    ac.nav_modes.clear();
    uint8_t nav_modes_byte = read_uint8(data, offset + 66);
    if (nav_modes_byte & 0x01) ac.nav_modes.push_back("autopilot");
    if (nav_modes_byte & 0x02) ac.nav_modes.push_back("vnav");
    if (nav_modes_byte & 0x04) ac.nav_modes.push_back("alt_hold");
    if (nav_modes_byte & 0x08) ac.nav_modes.push_back("approach");
    if (nav_modes_byte & 0x10) ac.nav_modes.push_back("lnav");
    if (nav_modes_byte & 0x20) ac.nav_modes.push_back("tcas");

    return true;
}

#endif // BINCRAFT2JSON_IMPL_HPP 