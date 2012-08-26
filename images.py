#!/usr/bin/env python2
import multiprocessing
import Image
import sys, os

def lastBits (n, count):
    """ Returns COUNT bits from number N """
    return n % (2**count)

def cleanBits (n, count):
    """ Cleans the last COUNT bits from number N """
    return n ^ lastBits (n, count)

def chopBits (n, x, y, z):
    """
    Chops the number n into the x, y, and z bits (Total bits must count to 8).
    Ex: number 243 (0b111.10.011) into 3, 2, 3 bits -> (7 (111), 2 (10), 3 (011))
    """
    first = (n >> (y + z)) % (2**x)
    middle = (n >> z) % (2**y)
    last = n % (2**z)
    return (first, middle, last)

def bitSum (bits, x, y, z):
    """
    Bits: tuple containig the hidden bits
    x, y, z: the bits they were from the image (same format as chopBits)
    """
    big = bits[0] << (y + z)
    med = bits[1] << z
    lit = bits[2]
    return big + med + lit

def add (effeduptuple):
    """
    This is the ugliest hack I've written in my life. I don't even remember
    what form the effeduptuple took. I think it was ((X, Y),(M, N))
    """
    neater = list (zip (effeduptuple[0], effeduptuple[1]))
    return map (lambda n: n[0] + n[1], neater)

def hidden(hidden):
    toadd = Image.open (hidden)
    toadd = toadd.convert("L") # We make the hidden image to be in 8bit-Grey
    im = toadd.size
    toadd = list (toadd.getdata())
    toadd = [ chopBits (toadd[n], 3, 2, 3)
        for n in range (im[1] * im[0]) ]
    return toadd

def carrier(origin):
    original = Image.open (origin)
    im = original.size
    original = list (original.getdata())
    original = [ (  cleanBits (original[n][0], 3), 
                    cleanBits (original[n][1], 2), 
                    cleanBits (original[n][2], 3) ) 
                for n in range (im[1] * im[0]) ]
    return original

def decode (image, x, y, z):
    im = Image.open(image)
    im = list (im.getdata())
    im = [ ( lastBits (I[0], x),
             lastBits (I[1], y),
             lastBits (I[2], z) )
            for I in im ]
    im = [ bitSum (N, x, y, z) for N in im ]
    return im

def main():
    pool = multiprocessing.Pool() # For the parallel map()
    if sys.argv[1] == "decode":
        source = Image.open(sys.argv[1])
        print ("Decoding the encoded...")
        secret = decode (sys.argv[1], 3, 2, 3)
        output = Image.new("L", source.size)
        output.putdata(secret)
        output.save(sys.argv[2])
    elif sys.argv[1] == "encode":
        im = Image.open(sys.argv[1])
        print ("Chopping Bits...")
        secret = hidden(sys.argv[1])
        print ("Cooking the Pot...")
        messenger = carrier(sys.argv[2])
        print ("Potting the Bits...")
        final = zip (secret, messenger)
        # In the first versions the variables used a disproportionate amount of
        # RAM
        del (secret)
        del (messenger)
        final = list (pool.map (add, final))
        final = list (pool.map (tuple, final))
        output = Image.new("RGB",im.size)
        output.putdata(final)
        output.save(sys.argv[3])

main()
