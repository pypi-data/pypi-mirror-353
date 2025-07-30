macsanity
======
A dangerously friendly tool to convert MAC addresses into whatever weird format the world throws at you.  
<br />  
<hr>

<h2 align="center">🧵 Our Story</h2>

<p align="center">
  <strong>macsanity</strong> started as an idea for compostable popsicles. </br>
  The working title was..</br>
  <strong>TurdVendor</strong> - <i>Where ethics meets excrement.</i></br></br>
  Goal: </br>save the planet — one regrettable dessert at a time.
</p>

<p align="center">
  That didn't really work out. </br>
  So we pivoted.
</p>

<p align="center">
  Now it’s a tool for formatting MAC addresses. </br>
  Because apparently, no two vendors can agree on what a colon is.
</p>

<p align="center">
  Still trying to save the world. </br>
  Just with slightly less shit.
</p>

<hr>

## How to use in terminal (cli)

### positional arguments:

mac_address: The MAC address to format

options:

-h, --help: show this help message and exit  
-f, --format: {'colon','dot','dash','ddash','space','blank','binary','compact','eui64','bpf','reverse','upsidedown'}, The format to use. If not specified, all formats will be printed.  
<br><br>
Available formats:<br>
**colon**       : Colon-separated format, e.g., ab:12:cd:34:ef:56.<br>
**dot**         : Dot notation, e.g., abcd.ef12.3456.<br>
**dash**        : Hyphen-separated format, e.g., ab-12-cd-34-ef-56.<br>
**ddash**       : Double-dash-separated format, e.g., ab12-cd34-ef56.<br>
**space**       : Space-separated format, e.g., ab 12 cd 34 ef 56.<br>
**blank**       : Continuous string with no delimiters, e.g., ab12cd34ef56.<br>
**binary**      : Binary format, e.g., 10101011 00010010 11001101 00110100 11101111 01010110.<br>
**compact**     : Base64 encoded format, e.g., qXLNTq9W.<br>
**eui64**       : Cisco EUI-64 format, e.g., ab12.cd34.fffe.ef56.<br>
**bpf**         : BPF format with each byte prefixed by '\\x', e.g., \\xab\\x12\\xcd\\x34\\xef\\x56.<br>
**reverse**     : Reverse byte order, e.g., 56ef34cd12ab.<br>
**upsidedown**  : Because why not? Flip your MAC and the world with it. 🌀<br><br>

-u, --uppercase: Prints the MAC address in uppercase.  
-l, --lowercase: Prints the MAC address in lowercase.

### Example usage:

```
macsanity abcdef123456 -f dot
```

output:

```
abcd.ef12.3456
```

There is also a shorter alias:

```
mcs abcd.ef12.3456 -f colon -u
```

output:

```
AB:CD:EF:12:34:56
```

## How to use in your code

```python
from macsanity import MacSanity

mac_address = 'ab:cd:ef:12:34:56'
mac = MacSanity(mac_address)

print(mac.dot)
print(mac.dash)
print(mac.ddash)
print(mac.space)
print(mac.colon)
print(mac.blank)
print(mac.binary)
print(mac.compact)
print(mac.eui64)
print(mac.bpf)
print(mac.reverse)
print(mac.upsidedown)
```

output:

```
abcd.ef12.3456  
ab-cd-ef-12-34-56  
abcd-ef12-3456  
ab cd ef 12 34 56  
ab:cd:ef:12:34:56  
abcdef123456  
10101011 11001101 11101111 00010010 00110100 01010110  
q83vEjRW  
ab12.cd34.fffe.ef56  
\xab\xcd\xef\x12\x34\x56  
654321fedcba  
ɓɐ ɟǝ pɔ ʞɾ ᴉu  
```
<hr>
<p align="center">
  <i>macsanity is proudly built by <a href="https://anython.dev" target="_blank"><strong>anython</strong></a>.</i><br />
  Because someone had to.
</p>
