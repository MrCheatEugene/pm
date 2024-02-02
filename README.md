# pm
PM is a messenger that really, really respects your privacy.

# How?
1. PM never, ever collects any logs of users that have ever connected to any PM's server.
2. PM does not request for any of your personal data like your phone number, full name, partial name, only PGP keys and your username.
3. PM encrypts your voice and messages using PGP, so nobody can listen to your conversation by intercepting the network.
4. PM server doesn't store your private keys. In fact, PM server itself does not have a private key at all. When you talk, or send a message, anybody that's talking in the same chat will encrypt the message with your specific public key, so only you can decrypt it.

# Pros and cons
```
+ No phone number required (like in Telegram/WhatsApp)
+ You set up the server, and you can be 100% confident in your privacy.
+ Fully open source
+ Free to use or modify
+ Server can be password-protected
+ Some basic server administration (still in progress)
- Limited to web
- Limited functionality (in comparison to Telegram or Whatsapp)
- Only VC mode
- Files aren't encrypted
```

# Set up
1. Clone the repo
2. `pip install websockets`
3. Configure the SSL certificates at line 115 of index.py, and passwords at line 14/15.
4. `python3 index.py`

# Usage
1. Go to any PM web interface (you can clone one from this repo, or use one on Github Pages)
2. Enter domain/IP of your or someone else's server
3. Connect
4. Done!

# License
This project is licensed by MIT license, but contains OpenPGPJS and MD5-JS libraries, that are licensed by LGPL 3.0 and MIT licenses.
