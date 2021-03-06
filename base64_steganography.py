import os
import sys
import codecs
import argparse

banner = """
┏━━┓┏━━━┳━━━┳━━━┳━━━┳┓╋┏┓┏━━━┳━━━━┳━━━┳━━━┳━━━┳━┓╋┏┳━━━┓
┃┏┓┃┃┏━┓┃┏━┓┃┏━━┫┏━━┫┃╋┃┃┃┏━┓┃┏┓┏┓┃┏━━┫┏━┓┃┏━┓┃┃┗┓┃┃┏━┓┃
┃┗┛┗┫┃╋┃┃┗━━┫┗━━┫┗━━┫┗━┛┃┃┗━━╋┛┃┃┗┫┗━━┫┃╋┗┫┃╋┃┃┏┓┗┛┃┃╋┃┃ 
┃┏━┓┃┗━┛┣━━┓┃┏━━┫┏━┓┣━━┓┃┗━━┓┃╋┃┃╋┃┏━━┫┃┏━┫┗━┛┃┃┗┓┃┃┃╋┃┃
┃┗━┛┃┏━┓┃┗━┛┃┗━━┫┗━┛┃╋╋┃┃┃┗━┛┃╋┃┃╋┃┗━━┫┗┻━┃┏━┓┃┃╋┃┃┃┗━┛┃
┗━━━┻┛╋┗┻━━━┻━━━┻━━━┛╋╋┗┛┗━━━┛╋┗┛╋┗━━━┻━━━┻┛╋┗┻┛╋┗━┻━━━┛
"""

alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

parser = argparse.ArgumentParser()

parser.add_argument('-v', "--verbose", help="Verbose mode", action="store_true")
parser.add_argument('-s', '--support', help="Support file that will be encoded", default=None, type=str)
parser.add_argument('-d', '--data', help="Data to be hidden", default=None, type=str)
parser.add_argument('-o', '--output', help="Output address of the encoded file", default=None, type=str)
parser.add_argument("--decode", help="Extract hidden text from a base64 file", action="store_true")
parser.add_argument("--include", help="Do not crop the last line of the base64 file (only if used while hidding data)", action="store_true")
args = parser.parse_args()

print(banner)

if not (args.decode):

    if ((args.data == None) or (args.support == None)):
        print("[-] Data and support files must be specified.")
        sys.exit(1)

    if args.verbose:
        print('[*] Opening files...')

    if not (os.path.exists(args.support)):
        print("[-] Error : Following file does not exist : " + args.support)
        sys.exit(1)

    if not (os.path.exists(args.data)):
        print("[-] Error : Following file does not exist : " + args.data)
        sys.exit(1)

    try:
        txtSupport = open(args.support, "rb")
    except:
        print("[-] Error while opening file : " + args.support)
        sys.exit(1)

    try:   
        txtSteg = open(args.data, "rb")
    except:
        print("[-] Error while opening file : " + args.data)
        sys.exit(1)

    bitsTextList = []
    bitsStegList = []
    bitsText = ''
    bitsSteg= ''

    if args.verbose:
        print('[*] Converting data to bits...')


    line = txtSteg.readline()

    while line:
        for i in range(len(line)):
            bitsStegList.append(bin(int(line[i]))[2:].zfill(8))
        line = txtSteg.readline()

    txtSteg.close()

    bitsSteg = ''.join(bitsStegList)

    line = txtSupport.readline()

    while line:
        for i in range(len(line)):
            bitsTextList.append(bin(int(line[i]))[2:].zfill(8))
        line = txtSupport.readline()

    txtSupport.close()

    bitsText = ''.join(bitsTextList)

    if (len(bitsText)/2 <= len(bitsSteg)):
        print("[-] Data too long for this support.")
        sys.exit(1)

    base64Parts = []

    bitsTextProcess = bitsText

    bitsStegProcess = bitsSteg

    if args.verbose:
        print('[*] Hidding data...')
    
    max_len = len(bitsStegProcess)

    while (len(bitsStegProcess) != 0):
        if (len(bitsStegProcess)%4==0):
            base64slice = ["=="]
            base64slice.append(bitsTextProcess[:8])
            bitsTextProcess = bitsTextProcess[8:]
            base64slice.append(bitsStegProcess[:4])
            bitsStegProcess = bitsStegProcess[4:] 
            base64Parts.append(base64slice)
        else:
            base64slice = ["="]
            base64slice.append(bitsTextProcess[:16])
            bitsTextProcess = bitsTextProcess[16:]
            base64slice.append(bitsStegProcess[:2])
            bitsStegProcess = bitsStegProcess[2:]
            base64Parts.append(base64slice)
        print(f'[*] {100*abs((len(bitsStegProcess)-max_len)/max_len):.2f}%',end='\r')

    print('[+] Data hidden.')

    if args.verbose:
        print('[*] Converting the end of support file...')

    if (len(bitsTextProcess)%6==0):
        base64slice=bitsTextProcess
        base64Parts.append(base64slice)
    elif(len(bitsTextProcess)%6==2):
        base64slice=["=="]
        base64slice.append(bitsTextProcess+'0000')
        base64Parts.append(base64slice)
    else:
        base64slice=["="]
        base64slice.append(bitsTextProcess+'00')
        base64Parts.append(base64slice)

    if args.verbose:
        print('[*] Converting bits to ASCII string...')

    base64lines = ''

    max_len = len(base64Parts)
    for i in range(len(base64Parts)):
        line = ''
        bitLineProcess = base64Parts[i]
        end = None
        if (bitLineProcess[0] != '0') and (bitLineProcess[0] != '1'):
            end = bitLineProcess[0]
            bitLineProcess = ''.join(bitLineProcess[1:])
        while(len(bitLineProcess) != 0):
            char = bitLineProcess[:6]
            bitLineProcess = bitLineProcess[6:]
            line += alphabet[int(char, 2)]
        if (end != None):
            line += end
        base64lines += line+'\n'
        print(f'[*] {100*abs((i)/max_len):.2f}%',end='\r')

    if args.verbose:
        print('[+] ASCII string build.')

    if (args.output != None):
        if args.verbose:
            print('[*] Writing base64 text at ' + args.output + '...')
        try:
            output = open(args.output,'w')
            output.write(base64lines)
            output.close()
            print("[+] Encoded string written at : " + args.output)
        except:
            print("[-] Error while creating ouput file.")
            sys.exit(1)
        sys.exit()
    else:
        print("[+] Encoded string : ")
        print(''.join(base64lines))
        sys.exit()

else:

    if (args.data == None):
        print("[-] Data file must be specified.")
        sys.exit(1)

    if args.verbose:
        print('[*] Opening files...')

    if not (os.path.exists(args.data)):
        print("[-] Error : Following file does not exist : " + args.data)
        sys.exit(1)

    try:   
        text = open(args.data, "r")
    except:
        print("[-] Error while opening file : " + args.data)
        sys.exit(1)

    
    line = text.readline()
    bitLines = []
    bits = ''
    while line:
        if (line[-2] == '='):
            bitText = ['==']
            for i in range(len(line) - 2):
                for k in range(len(alphabet)):
                    if alphabet[k] == line[i]:
                        bitText.append(bin(k)[2:].zfill(6))
            bitLines.append(bitText)
        elif (line[-1] == '='):
            bitText = ['=']
            for i in range(len(line) - 1):
                for k in range(len(alphabet)):
                    if alphabet[k] == line[i]:
                        bitText.append(bin(k)[2:].zfill(6))
            bitLines.append(bitText)
        else:
            for i in range(len(line)):
                for k in range(len(alphabet)):
                    if alphabet[k] == line[i]:
                        bitText.append(bin(k)[2:].zfill(6))
            bitLines.append(bitText)
        line = text.readline()
    text.close()

    if not args.include:
        bitLines=bitLines[:-1]

    if args.verbose:
        print('[*] Extracting data...')

    for line in bitLines:
        lastchar = line[-1]
        pad = line[0]
        if pad == '==':
            for bit in lastchar[-4:]:
                bits += bit
        elif pad == '=':
            for bit in lastchar[-2:]:
                bits += bit
    
    print("[+] Data extracted.")

    if args.verbose:
        print('[*] Converting bits to ASCII string...')

    try:
        plainText = codecs.decode(hex(int(bits, 2))[2:], 'hex').decode('ascii')
        plain = True
    except:
        try:
            print("[-] Error while converting bits to ASCII string.\n[*] Extracting raw bytes...")
            split_bits = [bits[index : index + 8] for index in range(0, len(bits), 8)]
            bytesString = b''
            for bitString in split_bits:
                bytesString += int(bitString, 2).to_bytes(1, byteorder='big')
            plain = False
        except:
            print("[-] Error while extracting raw bytes.")
            sys.exit(1)

    if (args.output != None):
        if args.verbose:
            print('[*] Writing extracted text at ' + args.output + '...')
        try:
            if plain:
                open(args.output,'w').write(plainText)
            else:
                open(args.output,'wb').write(bytesString)
            print("[+] Encoded string written at : " + args.output)
        except:
            print("[-] Error while creating ouput file.")
            sys.exit(1)
        sys.exit()
    else:
        print("[+] Extracted text : ")
        try:
            print(plainText)
        except:
            print(bytesString)
        sys.exit()