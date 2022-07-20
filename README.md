

### Context

As demonstrated in this [case study](https://community.sophos.com/sophos-labs/b/blog/posts/decoding-malicious-powershell), a common tactic actors deploy to conceal malicious powershell payloads and evade detection is to compress and encode the real payload with the following steps:

- Take the powershell payload and compress it.
- Base 64 encode[^1] the compressed script.
- Wrap the encoded, compressed payload in powershell which will decode, decompress, abd then execute, shown below:

```powershell
$s=New-Object IO.MemoryStream(,[Convert]::FromBase64String([ENCODED COMPRESSED PAYLOAD SCRIPT]));IEX (New-Object IO.StreamReader(New-Object IO.Compression.GzipStream($s,[IO.Compression.CompressionMode]::Decompress))).ReadToEnd();
```

- Finally Base 64 encode[^1] the 'wrapped' script above
- This final encoded string will then be executed with the -E (EncodedCommand) flag in some form

Note there is nothing preventing the final Base 64 encoded string being repeated through this process, as detailed below

 

### This Tool

This is a python tool to handle those three key functionalities:

- Compress powerhsell payloads
- Encode powershell scripts
- Wrap encoded compressed powershell scripts

Then as the compression/encoding/wrapping/encoding cycle is repeatable it allows an arbitrary number of cycles to be applied to any given payload 



### Usage

**WARNING**: Anti Virus may need to be temporarily disabled in order to run/work with these files

```
python encode_powershell.py -f <Path To Powershell Payload>
```

**Running the example**
Navigate to this directory and run
```
python encode_powershell.py -f "example/example.ps1" -o "example/encoded_example.ps1" -n 2
```
This will encode over two rounds a simple powershell script that creates a notification

[^1]: When executing encoded commands, powershell typically requires the Encoded string to decode to UTF-16LE (2000) strings, meaning the _original_ command string first needs converted to UTF-16LE, then subsequently Base 64 encoded.