#include "codec.hpp"
#include <iostream>
#include <array>
#include <sstream>

struct TestMessage
{
    std::uint8_t u8;
    std::int8_t i8;
    std::uint16_t u16;
    std::int16_t i16;
    std::uint32_t u32;
    std::int32_t i32;

    std::array<std::uint8_t, 3> arr_u8;
    std::array<std::int16_t, 2> arr_i16;
    std::array<codec::partbyte, 3> arr_pb;
    std::array<std::uint32_t, 2> arr_u32;
};

constexpr std::size_t messageSize = 32;

// Code as would be generated with python
std::uint8_t* encode(const TestMessage& message, std::uint8_t* buffer)
{
    buffer = codec::encode(message.u8, buffer);
    buffer = codec::encode(message.i8, buffer);
    buffer = codec::encode(message.u16, buffer);
    buffer = codec::encode(message.i16, buffer);
    buffer = codec::encode(message.u32, buffer);
    buffer = codec::encode(message.i32, buffer);
    buffer = codec::encode(message.arr_u8, buffer);
    buffer = codec::encode(message.arr_i16, buffer);
    buffer = codec::encode(message.arr_pb, buffer);
    buffer = codec::encode(message.arr_u32, buffer);
    return buffer;
}

const std::uint8_t* decode(TestMessage& message, const std::uint8_t* buffer)
{
    buffer = codec::decode(message.u8, buffer);
    buffer = codec::decode(message.i8, buffer);
    buffer = codec::decode(message.u16, buffer);
    buffer = codec::decode(message.i16, buffer);
    buffer = codec::decode(message.u32, buffer);
    buffer = codec::decode(message.i32, buffer);
    buffer = codec::decode(message.arr_u8, buffer);
    buffer = codec::decode(message.arr_i16, buffer);
    buffer = codec::decode(message.arr_pb, buffer);
    buffer = codec::decode(message.arr_u32, buffer);
    return buffer;
}

std::uint8_t* encode_be(const TestMessage& message, std::uint8_t* buffer)
{
    buffer = codec::encode_be(message.u8, buffer);
    buffer = codec::encode_be(message.i8, buffer);
    buffer = codec::encode_be(message.u16, buffer);
    buffer = codec::encode_be(message.i16, buffer);
    buffer = codec::encode_be(message.u32, buffer);
    buffer = codec::encode_be(message.i32, buffer);
    buffer = codec::encode_be(message.arr_u8, buffer);
    buffer = codec::encode_be(message.arr_i16, buffer);
    buffer = codec::encode_be(message.arr_pb, buffer);
    buffer = codec::encode_be(message.arr_u32, buffer);
    return buffer;
}

const std::uint8_t* decode_be(TestMessage& message, const std::uint8_t* buffer)
{
    buffer = codec::decode_be(message.u8, buffer);
    buffer = codec::decode_be(message.i8, buffer);
    buffer = codec::decode_be(message.u16, buffer);
    buffer = codec::decode_be(message.i16, buffer);
    buffer = codec::decode_be(message.u32, buffer);
    buffer = codec::decode_be(message.i32, buffer);
    buffer = codec::decode_be(message.arr_u8, buffer);
    buffer = codec::decode_be(message.arr_i16, buffer);
    buffer = codec::decode_be(message.arr_pb, buffer);
    buffer = codec::decode_be(message.arr_u32, buffer);
    return buffer;
}

std::string printPayload(std::uint8_t* buffer, std::uint8_t* end)
{
    std::stringstream out;
    out << std::hex;
    for(; buffer != end; ++buffer)
    {
        out << static_cast<int>(*buffer) << " ";
    }
    return out.str();
}

template<typename T, std::size_t N>
std::ostream& operator<<(std::ostream& out, std::array<T, N> x)
{
    for(auto i : x)
    {
        out << (int)i << ", ";
    }
    return out;
}

namespace ns_1
{
    struct Message
    {
        std::uint16_t x;
    };

    std::uint8_t* encode(const Message& message, std::uint8_t* buffer)
    {
        buffer = codec::encode_any(message.x, buffer);
        return buffer;
    }

    const std::uint8_t* decode(Message& message, const std::uint8_t* buffer)
    {
        buffer = codec::decode_any(message.x, buffer);
        return buffer;
    }
}

namespace ns_2
{
    struct Message
    {
        ns_1::Message x;
        std::uint16_t y;
    };

    std::uint8_t* encode(const Message& message, std::uint8_t* buffer)
    {
        buffer = codec::encode_any(message.x, buffer);
        buffer = codec::encode_any(message.y, buffer);
        return buffer;
    }

    const std::uint8_t* decode(Message& message, const std::uint8_t* buffer)
    {
        buffer = codec::decode_any(message.x, buffer);
        buffer = codec::decode_any(message.y, buffer);
        return buffer;
    }
}

int main()
{
    try
    {
        std::array<std::uint8_t, messageSize> payload = { 
            0x16,
            0xDF, 
            0x34, 0x12,
            0x9C, 0xFF,
            0xFF, 0x00, 0xCD, 0xAB,
            0xF0, 0xD8, 0xFF, 0xFF,
            0x01, 0x02, 0x03,
            0x16, 0x00, 0xDF, 0xFF,
			0X22, 0x33, 0x44,
            0xDD, 0xCC, 0xBB, 0xAA, 0x44, 0x33, 0x22, 0x11
        };

        {
            TestMessage message{ 22, -33, 0x1234, -100, 0xABCD00FF, -10000, {1, 2, 3}, {22, -33}, {0x22, 0x33, 0x44}, {0xAABBCCDD, 0x11223344} };

            std::array<std::uint8_t, messageSize> buffer{};

            std::uint8_t* end = encode(message, buffer.data());


            if(end != buffer.data() + messageSize)
            {
                std::cout << "Encode TestMessage failed: incorrect payload size: " << end - buffer.data() << "\n";
            }
            if(buffer != payload)
            {
                std::cout << "Encode TestMessage failed: incorrect payload: " << printPayload(buffer.data(), end) << "\n";
            }
        }
        {
            TestMessage decoded{};
            const std::uint8_t* end = decode(decoded, payload.data());

            if(end != payload.data() + messageSize)
            {
                std::cout << "Decode TestMessage failed: incorrect payload size: " << end - payload.data() << "\n";
            }
            if(decoded.u8 != 22)
            {
                std::cout << "Decode TestMessage failed: incorrect u8: " << (int)decoded.u8 << "\n";
            }
            if(decoded.i8 != -33)
            {
                std::cout << "Decode TestMessage failed: incorrect i8: " << (int)decoded.i8 << "\n";
            }
            if(decoded.u16 != 0x1234)
            {
                std::cout << "Decode TestMessage failed: incorrect u16: " << decoded.u16 << "\n";
            }
            if(decoded.i16 != -100)
            {
                std::cout << "Decode TestMessage failed: incorrect i16: " << decoded.i16 << "\n";
            }
            if(decoded.u32 != 0xABCD00FF)
            {
                std::cout << "Decode TestMessage failed: incorrect u32: " << decoded.u32 << "\n";
            }
            if(decoded.i32 != -10000)
            {
                std::cout << "Decode TestMessage failed: incorrect i32: " << decoded.i32 << "\n";
            }
            if(decoded.arr_u8 != std::array<std::uint8_t, 3>{1, 2, 3})
            {
                std::cout << "Decode TestMessage failed: incorrect arr_u8: " << decoded.arr_u8 << "\n";
            }
            if(decoded.arr_i16 != std::array<std::int16_t, 2>{22, -33})
            {
                std::cout << "Decode TestMessage failed: incorrect arr_i16: " << decoded.arr_i16 << "\n";
            }
            if(decoded.arr_pb != std::array<codec::partbyte, 3>{0x22, 0x33, 0x44})
            {
                std::cout << "Decode TestMessage failed: incorrect arr_pb: " << decoded.arr_pb << "\n";
            }
            if (decoded.arr_u32 != std::array<std::uint32_t, 2>{0xAABBCCDD, 0x11223344})
            {
                std::cout << "Decode TestMessage failed: incorrect arr_u32: " << decoded.arr_pb << "\n";
            }
        }
        {
            ns_2::Message message{{0xABCD}, 0x1234};

            std::array<std::uint8_t, 4> buffer = {};
            std::uint8_t* end = codec::encode_any(message, buffer.data());
            
            std::array<std::uint8_t, 4> expected = { 0xCD, 0xAB, 0x34, 0x12 };
            if(end != buffer.data() + 4)
            {
                std::cout << "Namespace test failed: incorrect payload size: " << end - buffer.data() << "\n";
            }
            if(buffer != expected)
            {
                std::cout << "Namespace test failed: incorrect payload: " << printPayload(buffer.data(), end) << "\n";
            }
            
            ns_2::Message decoded{{0}, 0};
            const std::uint8_t* end2 = codec::decode_any(decoded, expected.data());
            if(end2 != expected.data() + 4)
            {
                std::cout << "Namespace test failed: incorrect payload size: " << end2 - expected.data() << "\n";
            }
            if(decoded.x.x != 0xABCD)
            {
                std::cout << "Namespace test failed: incorrect x: " << (int)decoded.x.x << "\n";
            }
            if(decoded.y != 0x1234)
            {
                std::cout << "Namespace test failed: incorrect y: " << (int)decoded.y << "\n";
            }
        }
		
        std::array<std::uint8_t, messageSize> payload_bigendian = { 
            0x16,
			0xDF, 
            0x12, 0x34,
			0xFF, 0x9C,
            0xAB, 0xCD, 0x00, 0xFF,    
			0xFF, 0xFF, 0xD8, 0xF0,   
            0x01, 0x02, 0x03,
            0x00, 0x16, 0xFF, 0xDF,
			0x44, 0x33, 0X22,
            0xAA, 0xBB, 0xCC, 0xDD, 0x11, 0x22, 0x33, 0x44
        };
		
        {
            TestMessage message{ 22, -33, 0x1234, -100, 0xABCD00FF, -10000, {1, 2, 3}, {22, -33}, {0x22, 0x33, 0x44}, {0xAABBCCDD, 0x11223344} };

            std::array<std::uint8_t, messageSize> buffer{};

            std::uint8_t* end = encode_be(message, buffer.data());

            if(end != buffer.data() + messageSize)
            {
                std::cout << "Encode BIG TestMessage failed: incorrect payload size: " << end - buffer.data() << "\n";
            }
            if(buffer != payload_bigendian)
            {
                std::cout << "Encode BIG TestMessage failed: incorrect payload: " << printPayload(buffer.data(), end) << "\n";
            }
        }
        {
            TestMessage decoded{};
            const std::uint8_t* end = decode_be(decoded, payload_bigendian.data());

            if(end != payload_bigendian.data() + messageSize)
            {
                std::cout << "Decode BIG TestMessage failed: incorrect payload size: " << end - payload_bigendian.data() << "\n";
            }
            if(decoded.u8 != 22)
            {
                std::cout << "Decode BIG TestMessage failed: incorrect u8: " << (int)decoded.u8 << "\n";
            }
            if(decoded.i8 != -33)
            {
                std::cout << "Decode BIG TestMessage failed: incorrect i8: " << (int)decoded.i8 << "\n";
            }
            if(decoded.u16 != 0x1234)
            {
                std::cout << "Decode BIG TestMessage failed: incorrect u16: " << decoded.u16 << "\n";
            }
            if(decoded.i16 != -100)
            {
                std::cout << "Decode BIG TestMessage failed: incorrect i16: " << decoded.i16 << "\n";
            }
            if(decoded.u32 != 0xABCD00FF)
            {
                std::cout << "Decode BIG TestMessage failed: incorrect u32: " << decoded.u32 << "\n";
            }
            if(decoded.i32 != -10000)
            {
                std::cout << "Decode BIG TestMessage failed: incorrect i32: " << decoded.i32 << "\n";
            }
            if(decoded.arr_u8 != std::array<std::uint8_t, 3>{1, 2, 3})
            {
                std::cout << "Decode BIG TestMessage failed: incorrect arr_u8: " << decoded.arr_u8 << "\n";
            }
            if(decoded.arr_i16 != std::array<std::int16_t, 2>{22, -33})
            {
                std::cout << "Decode BIG TestMessage failed: incorrect arr_i16: " << decoded.arr_i16 << "\n";
            }
            if(decoded.arr_pb != std::array<codec::partbyte, 3>{0x22, 0x33, 0x44})
            {
                std::cout << "Decode BIG TestMessage failed: incorrect arr_pb: " << decoded.arr_pb << "\n";
            }
            if (decoded.arr_u32 != std::array<std::uint32_t, 2>{0xAABBCCDD, 0x11223344})
            {
                std::cout << "Decode BIG TestMessage failed: incorrect arr_u32: " << decoded.arr_pb << "\n";
            }
        }
    }
    catch(std::exception& e)
    {
        std::cout << "Exception : " << e.what() << "\n";
    }
    std::cout << "Tests end\n";
}
