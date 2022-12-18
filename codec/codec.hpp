#pragma once

#include <cstdint>
#include <array>
#include <string.h>
#include <type_traits>

namespace codec
{
namespace detail
{
template<typename T>
constexpr bool is_small_integral = std::is_integral_v<T> && sizeof(T) <= 4;
}


// Arrays of partbyte are treated as big integer that needs reverse byte order in big endian
struct partbyte
{
    uint8_t v;

    partbyte() = default;
    partbyte(const partbyte&) = default;
    partbyte(partbyte&&) = default;
    partbyte& operator=(const partbyte&) = default;
    partbyte& operator=(partbyte&&) = default;

    partbyte(uint8_t x) : v{ x } {}
    partbyte& operator=(uint8_t x) { v = x; return *this; }

    operator uint8_t () const { return v; }
	
	bool operator==(partbyte x) const { return v == x.v; }
	bool operator!=(partbyte x) const { return v != x.v; }
	bool operator< (partbyte x) const { return v <  x.v; }
	bool operator<=(partbyte x) const { return v <= x.v; }
	bool operator> (partbyte x) const { return v >  x.v; }
	bool operator>=(partbyte x) const { return v >= x.v; }
};

inline std::uint8_t* encode(std::uint8_t data, std::uint8_t* buffer)
{
    buffer[0] = data;
    return buffer + 1;
}

inline std::uint8_t* encode(std::int8_t data, std::uint8_t* buffer)
{
    buffer[0] = *reinterpret_cast<std::uint8_t*>(&data);
    return buffer + 1;
}

inline std::uint8_t* encode(std::uint16_t data, std::uint8_t* buffer)
{
    std::uint8_t* x = reinterpret_cast<std::uint8_t*>(&data);
    buffer[0] = *x;
    buffer[1] = *(x + 1);
    return buffer + 2;
}

inline std::uint8_t* encode(std::int16_t data, std::uint8_t* buffer)
{
    std::uint8_t* x = reinterpret_cast<std::uint8_t*>(&data);
    buffer[0] = *x;
    buffer[1] = *(x + 1);
    return buffer + 2;
}

inline std::uint8_t* encode(std::uint32_t data, std::uint8_t* buffer)
{
    std::uint8_t* x = reinterpret_cast<std::uint8_t*>(&data);
    memcpy(buffer, x, 4);
    return buffer + 4;
}

inline std::uint8_t* encode(std::int32_t data, std::uint8_t* buffer)
{
    std::uint8_t* x = reinterpret_cast<std::uint8_t*>(&data);
    memcpy(buffer, x, 4);
    return buffer + 4;
}

template<typename T, std::size_t N, std::enable_if_t<!detail::is_small_integral<T>, int> = 0>
inline std::uint8_t* encode(const std::array<T, N>& data, std::uint8_t* buffer)
{
    for(auto x: data)
    {
        buffer = encode(x, buffer);
    }
    return buffer;
}

template<typename T, std::size_t N, std::enable_if_t<detail::is_small_integral<T>, int> = 0>
inline std::uint8_t* encode(const std::array<T, N>& data, std::uint8_t* buffer)
{
    memcpy(buffer, data.data(), N * sizeof(T));
    return buffer + N * sizeof(T);
}

template<std::size_t N>
inline std::uint8_t* encode(const std::array<partbyte, N>& data, std::uint8_t* buffer)
{
    memcpy(buffer, data.data(), N);
    return buffer + N;
}

template<typename T>
inline std::uint8_t* encode_any(const T& data, std::uint8_t* buffer)
{
    return encode(data, buffer); // Hopes to find correct function with ADL
}

// ================================================================ //
// ================================================================ //

inline const std::uint8_t* decode(std::uint8_t& data, const std::uint8_t* buffer)
{
    data = buffer[0];
    return buffer + 1;
}

inline const std::uint8_t* decode(std::int8_t& data, const std::uint8_t* buffer)
{
    data = *reinterpret_cast<const std::int8_t*>(&buffer[0]);
    return buffer + 1;
}

inline const std::uint8_t* decode(std::uint16_t& data, const std::uint8_t* buffer)
{
    std::uint8_t* x = reinterpret_cast<std::uint8_t*>(&data);
    *x = buffer[0];
    *(x + 1) = buffer[1];
    return buffer + 2;
}

inline const std::uint8_t* decode(std::int16_t& data, const std::uint8_t* buffer)
{
    std::uint8_t* x = reinterpret_cast<std::uint8_t*>(&data);
    *x = buffer[0];
    *(x + 1) = buffer[1];
    return buffer + 2;
}

inline const std::uint8_t* decode(std::uint32_t& data, const std::uint8_t* buffer)
{
    std::uint8_t* x = reinterpret_cast<std::uint8_t*>(&data);
    memcpy(x, buffer, 4);
    return buffer + 4;
}

inline const std::uint8_t* decode(std::int32_t& data, const std::uint8_t* buffer)
{
    std::uint8_t* x = reinterpret_cast<std::uint8_t*>(&data);
    memcpy(x, buffer, 4);
    return buffer + 4;
}

template<typename T, std::size_t N, std::enable_if_t<!detail::is_small_integral<T>, int> = 0>
inline const std::uint8_t* decode(std::array<T, N>& data, const std::uint8_t* buffer)
{
    for(T& x: data)
    {
        buffer = decode(x, buffer);
    }
    return buffer;
}

template<typename T, std::size_t N, std::enable_if_t<detail::is_small_integral<T>, int> = 0>
inline const std::uint8_t* decode(std::array<T, N>& data, const std::uint8_t* buffer)
{
    memcpy(data.data(), buffer, N * sizeof(T));
    return buffer + N * sizeof(T);
}

template<std::size_t N>
inline const std::uint8_t* decode(std::array<partbyte, N>& data, const std::uint8_t* buffer)
{
    memcpy(data.data(), buffer, N);
    return buffer + N;
}

template<typename T>
inline const std::uint8_t* decode_any(T& data, const std::uint8_t* buffer)
{
    return decode(data, buffer); // Hopes to find correct function with ADL
}

// ================================================================ //
// ================================================================ //

inline std::uint8_t* encode_be(std::uint8_t data, std::uint8_t* buffer)
{
    buffer[0] = data;
    return buffer + 1;
}

inline std::uint8_t* encode_be(std::int8_t data, std::uint8_t* buffer)
{
    buffer[0] = *reinterpret_cast<std::uint8_t*>(&data);
    return buffer + 1;
}

inline std::uint8_t* encode_be(std::uint16_t data, std::uint8_t* buffer)
{
    std::uint8_t* x = reinterpret_cast<std::uint8_t*>(&data);
    buffer[0] = *(x + 1);
    buffer[1] = *(x + 0);
    return buffer + 2;
}

inline std::uint8_t* encode_be(std::int16_t data, std::uint8_t* buffer)
{
    std::uint8_t* x = reinterpret_cast<std::uint8_t*>(&data);
    buffer[0] = *(x + 1);
    buffer[1] = *(x + 0);
    return buffer + 2;
}

inline std::uint8_t* encode_be(std::uint32_t data, std::uint8_t* buffer)
{
    std::uint8_t* x = reinterpret_cast<std::uint8_t*>(&data);
    buffer[0] = *(x + 3);
    buffer[1] = *(x + 2);
    buffer[2] = *(x + 1);
    buffer[3] = *(x + 0);
    return buffer + 4;
}

inline std::uint8_t* encode_be(std::int32_t data, std::uint8_t* buffer)
{
    std::uint8_t* x = reinterpret_cast<std::uint8_t*>(&data);
    buffer[0] = *(x + 3);
    buffer[1] = *(x + 2);
    buffer[2] = *(x + 1);
    buffer[3] = *(x + 0);
    return buffer + 4;
}

template<typename T, std::size_t N>
inline std::uint8_t* encode_be(const std::array<T, N>& data, std::uint8_t* buffer)
{
    for (auto x : data)
    {
        buffer = encode_be(x, buffer);
    }
    return buffer;
}

template<std::size_t N>
inline std::uint8_t* encode_be(const std::array<std::uint8_t, N>& data, std::uint8_t* buffer)
{
    memcpy(buffer, data.data(), N);
    return buffer + N;
}

template<std::size_t N>
inline std::uint8_t* encode_be(const std::array<partbyte, N>& data, std::uint8_t* buffer)
{
    std::copy(data.rbegin(), data.rend(), buffer);
    return buffer + N;
}

template<typename T>
inline std::uint8_t* encode_any_be(const T& data, std::uint8_t* buffer)
{
    return encode_be(data, buffer); // Hopes to find correct function with ADL
}

// ================================================================ //
// ================================================================ //

inline const std::uint8_t* decode_be(std::uint8_t& data, const std::uint8_t* buffer)
{
    data = buffer[0];
    return buffer + 1;
}

inline const std::uint8_t* decode_be(std::int8_t& data, const std::uint8_t* buffer)
{
    data = *reinterpret_cast<const std::int8_t*>(&buffer[0]);
    return buffer + 1;
}

inline const std::uint8_t* decode_be(std::uint16_t& data, const std::uint8_t* buffer)
{
    std::uint8_t* x = reinterpret_cast<std::uint8_t*>(&data);
    *(x + 1) = buffer[0];
    *(x + 0) = buffer[1];
    return buffer + 2;
}

inline const std::uint8_t* decode_be(std::int16_t& data, const std::uint8_t* buffer)
{
    std::uint8_t* x = reinterpret_cast<std::uint8_t*>(&data);
    *(x + 1) = buffer[0];
    *(x + 0) = buffer[1];
    return buffer + 2;
}

inline const std::uint8_t* decode_be(std::uint32_t& data, const std::uint8_t* buffer)
{
    std::uint8_t* x = reinterpret_cast<std::uint8_t*>(&data);
    *(x + 3) = buffer[0];
    *(x + 2) = buffer[1];
    *(x + 1) = buffer[2];
    *(x + 0) = buffer[3];
    return buffer + 4;
}

inline const std::uint8_t* decode_be(std::int32_t& data, const std::uint8_t* buffer)
{
    std::uint8_t* x = reinterpret_cast<std::uint8_t*>(&data);
    *(x + 3) = buffer[0];
    *(x + 2) = buffer[1];
    *(x + 1) = buffer[2];
    *(x + 0) = buffer[3];
    return buffer + 4;
}

template<typename T, std::size_t N>
inline const std::uint8_t* decode_be(std::array<T, N>& data, const std::uint8_t* buffer)
{
    for (T& x : data)
    {
        buffer = decode_be(x, buffer);
    }
    return buffer;
}

template<std::size_t N>
inline const std::uint8_t* decode_be(std::array<std::uint8_t, N>& data, const std::uint8_t* buffer)
{
    memcpy(data.data(), buffer, N);
    return buffer + N;
}

template<std::size_t N>
inline const std::uint8_t* decode_be(std::array<partbyte, N>& data, const std::uint8_t* buffer)
{
    std::copy(buffer, buffer + N, data.rbegin());
    return buffer + N;
}

template<typename T>
inline const std::uint8_t* decode_any_be(T& data, const std::uint8_t* buffer)
{
    return decode_be(data, buffer); // Hopes to find correct function with ADL
}

}
