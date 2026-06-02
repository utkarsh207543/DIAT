"""
Utility Functions

Converted from utilities.c
"""

import os
import math
from config import *
from cephes import cephes_erfc


def is_zero(x):
    """Check if value is zero"""
    return abs(x) < 1e-10


def is_negative(x):
    """Check if value is negative"""
    return x < 0.0


def is_greater_than_one(x):
    """Check if value is greater than one"""
    return x > 1.0


def display_generator_options():
    """Display generator selection menu"""
    print("           G E N E R A T O R    S E L E C T I O N")
    print("           ______________________________________\n")
    print("    [0] Input File                 [1] Linear Congruential")
    print("    [2] Quadratic Congruential I   [3] Quadratic Congruential II")
    print("    [4] Cubic Congruential         [5] XOR")
    print("    [6] Modular Exponentiation     [7] Blum-Blum-Shub")
    print("    [8] Micali-Schnorr             [9] G Using SHA-1\n")
    
    option = int(input("   Enter Choice: "))
    print("\n")
    return option


def generator_options():
    """Get generator selection from user"""
    option = NUMOFGENERATORS + 1
    stream_file = None
    
    while option < 0 or option > NUMOFGENERATORS:
        option = display_generator_options()
        
        if option == 0:
            file = input("\t\tUser Prescribed Input File: ")
            stream_file = file
            print()
            if not os.path.exists(stream_file):
                print(f"File Error:  file {stream_file} could not be opened.")
                exit(-1)
        elif option == 1:
            stream_file = "Linear-Congruential"
        elif option == 2:
            stream_file = "Quadratic-Congruential-1"
        elif option == 3:
            stream_file = "Quadratic-Congruential-2"
        elif option == 4:
            stream_file = "Cubic-Congruential"
        elif option == 5:
            stream_file = "XOR"
        elif option == 6:
            stream_file = "Modular-Exponentiation"
        elif option == 7:
            stream_file = "Blum-Blum-Shub"
        elif option == 8:
            stream_file = "Micali-Schnorr"
        elif option == 9:
            stream_file = "G using SHA-1"
        else:
            print("Error:  Out of range - Try again!")
    
    return option, stream_file


def choose_tests():
    """Allow user to choose which tests to run"""
    global test_vector
    
    print("                S T A T I S T I C A L   T E S T S")
    print("                _________________________________\n")
    print("    [01] Frequency                       [02] Block Frequency")
    print("    [03] Cumulative Sums                 [04] Runs")
    print("    [05] Longest Run of Ones             [06] Rank")
    print("    [07] Discrete Fourier Transform      [08] Nonperiodic Template Matchings")
    print("    [09] Overlapping Template Matchings  [10] Universal Statistical")
    print("    [11] Approximate Entropy             [12] Random Excursions")
    print("    [13] Random Excursions Variant       [14] Serial")
    print("    [15] Linear Complexity\n")
    print("         INSTRUCTIONS")
    print("            Enter 0 if you DO NOT want to apply all of the")
    print("            statistical tests to each sequence and 1 if you DO.\n")
    
    test_vector[0] = int(input("   Enter Choice: "))
    print()
    
    if test_vector[0] == 1:
        for i in range(1, NUMOFTESTS + 1):
            test_vector[i] = 1
    else:
        print("         INSTRUCTIONS")
        print("            Enter a 0 or 1 to indicate whether or not the numbered statistical")
        print("            test should be applied to each sequence.\n")
        print("      123456789111111")
        print("               012345")
        print("      ", end="")
        
        test_input = input()
        for i in range(1, min(len(test_input) + 1, NUMOFTESTS + 1)):
            test_vector[i] = int(test_input[i - 1])
        print("\n")


def fix_parameters():
    """Allow user to adjust test parameters"""
    global tp
    
    # Check if any parameterized tests are selected
    if (test_vector[TEST_BLOCK_FREQUENCY] != 1 and test_vector[TEST_NONPERIODIC] != 1 and
            test_vector[TEST_OVERLAPPING] != 1 and test_vector[TEST_APEN] != 1 and
            test_vector[TEST_SERIAL] != 1 and test_vector[TEST_LINEARCOMPLEXITY] != 1):
        return
    
    while True:
        counter = 1
        print("        P a r a m e t e r   A d j u s t m e n t s")
        print("        -----------------------------------------")
        
        if test_vector[TEST_BLOCK_FREQUENCY] == 1:
            print(f"    [{counter}] Block Frequency Test - block length(M):         {tp.blockFrequencyBlockLength}")
            counter += 1
        if test_vector[TEST_NONPERIODIC] == 1:
            print(f"    [{counter}] NonOverlapping Template Test - block length(m): {tp.nonOverlappingTemplateBlockLength}")
            counter += 1
        if test_vector[TEST_OVERLAPPING] == 1:
            print(f"    [{counter}] Overlapping Template Test - block length(m):    {tp.overlappingTemplateBlockLength}")
            counter += 1
        if test_vector[TEST_APEN] == 1:
            print(f"    [{counter}] Approximate Entropy Test - block length(m):     {tp.approximateEntropyBlockLength}")
            counter += 1
        if test_vector[TEST_SERIAL] == 1:
            print(f"    [{counter}] Serial Test - block length(m):                  {tp.serialBlockLength}")
            counter += 1
        if test_vector[TEST_LINEARCOMPLEXITY] == 1:
            print(f"    [{counter}] Linear Complexity Test - block length(M):       {tp.linearComplexitySequenceLength}")
            counter += 1
        
        print()
        testid = int(input("   Select Test (0 to continue): "))
        print()
        
        if testid == 0:
            break
        
        counter = 0
        if test_vector[TEST_BLOCK_FREQUENCY] == 1:
            counter += 1
            if counter == testid:
                tp.blockFrequencyBlockLength = int(input("   Enter Block Frequency Test block length: "))
                print()
                continue
        
        if test_vector[TEST_NONPERIODIC] == 1:
            counter += 1
            if counter == testid:
                tp.nonOverlappingTemplateBlockLength = int(input("   Enter NonOverlapping Template Test block Length: "))
                print()
                continue
        
        if test_vector[TEST_OVERLAPPING] == 1:
            counter += 1
            if counter == testid:
                tp.overlappingTemplateBlockLength = int(input("   Enter Overlapping Template Test block Length: "))
                print()
                continue
        
        if test_vector[TEST_APEN] == 1:
            counter += 1
            if counter == testid:
                tp.approximateEntropyBlockLength = int(input("   Enter Approximate Entropy Test block Length: "))
                print()
                continue
        
        if test_vector[TEST_SERIAL] == 1:
            counter += 1
            if counter == testid:
                tp.serialBlockLength = int(input("   Enter Serial Test block Length: "))
                print()
                continue
        
        if test_vector[TEST_LINEARCOMPLEXITY] == 1:
            counter += 1
            if counter == testid:
                tp.linearComplexitySequenceLength = int(input("   Enter Linear Complexity Test block Length: "))
                print()
                continue


def open_output_streams(option):
    """Open output file streams"""
    global freqfp, summary, stats, results
    
    os.makedirs(f"experiments/{generator_dir[option]}", exist_ok=True)
    
    freqfn = f"experiments/{generator_dir[option]}/freq.txt"
    freqfp = open(freqfn, 'w')
    
    summaryfn = f"experiments/{generator_dir[option]}/finalAnalysisReport.txt"
    summary = open(summaryfn, 'w')
    
    for i in range(1, NUMOFTESTS + 1):
        if test_vector[i] == 1:
            os.makedirs(f"experiments/{generator_dir[option]}/{test_names[i]}", exist_ok=True)
            
            stats_dir = f"experiments/{generator_dir[option]}/{test_names[i]}/stats.txt"
            results_dir = f"experiments/{generator_dir[option]}/{test_names[i]}/results.txt"
            
            stats[i] = open(stats_dir, 'w')
            results[i] = open(results_dir, 'w')
    
    num_of_bit_streams = int(input("   How many bitstreams? "))
    tp.numOfBitStreams = num_of_bit_streams
    print()


def convert_to_bits(x, xBitLength, bitsNeeded, num_0s, num_1s, bitsRead):
    """Convert bytes to bits"""
    global epsilon
    
    count = 0
    zeros = 0
    ones = 0
    
    for i in range((xBitLength + 7) // 8):
        mask = 0x80
        for j in range(8):
            if x[i] & mask:
                bit = 1
                num_1s[0] += 1
                ones += 1
            else:
                bit = 0
                num_0s[0] += 1
                zeros += 1
            
            mask >>= 1
            epsilon[bitsRead[0]] = bit
            bitsRead[0] += 1
            
            if bitsRead[0] == bitsNeeded:
                return 1
            
            count += 1
            if count == xBitLength:
                return 0
    
    return 0
