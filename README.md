# SSH CA Client

Client for interacting with [SSH CA Server](https://github.com/commercehub-oss/ssh-ca-server).


## Installation instructions

1. Install ca-client
    ```
    pip install ca-client
    ```

## Client Usage

ca-client is used to interact with the [SSH CA server]((https://github.com/commercehub-oss/ssh-ca-server)).  The client uses HTTP auth to verify identity and provides facilities for listing roles, signing public keys and getting CA certificates.

After completing a signing request ca-client will load the signed certificate and private key into memory with ssh-agent.  ssh-agent will sling certs at a remote host until a successful challenge response occurs granting access to the remote host.  By default sshd will reject the client after 5 failed attempts.  ca-client will not load a certificate with ssh-agent if it will exceed 5 active certificates.  The private key and signed certificate must be loaded with ssh-agent and both count towards the limit of 5.

Certificates loaded with ssh-agent do not persist a reboot.  Following a reboot you can reload using ssh-add or initiate a new signing request with ca-client.


The first time ca-client is executed you must provide the FQDN of the CA server and the default certificate authority to use when issueing a signing request.

```
$ ca-client
 
Failed to load configuration from /Users/username/.ca-client/config.json
Enter FQDN of CA Server: ca-server.mydomain.com
Enter name of default CA: nonproduction
Loading configuration from /Users/username/.ca-client/config.json
```

Client configuration example:
```
$ cat ~/.ca-client/config.json
 
{
  "DEFAULT_CA": "nonproduction",
  "BASE_URL": "https://ca-server.mydomain.com"
}
```

ca-client command line usage:
```
usage: ca-client [-h] [-s CA | -r | -c | -k CA]
 
Tool to sign your public SSH key
 
optional arguments:
	-h, --help           show this help message and exit
	-s CA, --sign CA     certificate signing request
	-u USER, --user USER  optional username for signing request
	-r, --list-roles     list my authorized roles
	-c, --list-cas       list available CAs
	-k CA, --get-key CA  list public key for CA
```

List your authorized roles:
```
$ ca-client -r
 
Role:                ssh-admin-group
Description:         Super Admin Role
Allowed Principals:  admin
Allowed CAs:         production,nonproduction
```

List available certificate authorities:
```
$ ca-client -c
 
CA name:         nonproduction
Max duration:    30d
 
CA name:         production
Max duration:    24h
```

Initiate signing request for the nonproduction certificate authority:
```
$ ca-client -s nonproduction
Please enter password for username:
 
/Users/username/.ssh/nonproduction_rsa-cert.pub updated
 
Identity added: /Users/username/.ssh/nonproduction_rsa (/Users/username/.ssh/nonproduction_rsa)
Certificate added: /Users/username/.ssh/nonproduction_rsa-cert.pub (username)
Identity loaded for current session but ssh-agent will not persist identities on reboot
 
If using bash you can add the following command to your .bash_profile
ssh-add /Users/username/.ssh/nonproduction_rsa
```

The ca-client will create a unique keypair for each of the requested certificate authorities within the users .ssh folder.

Example users .ssh folder after requesting certs from production and nonproduction certificate authority.
```
$ ls ~/.ssh
 
nonproduction_rsa          nonproduction_rsa-cert.pub nonproduction_rsa.pub
production_rsa             production_rsa-cert.pub    production_rsa.pub
```

The below examples shows the result of a successfully signed SSH certificate:

```
$ ssh-keygen -L -f ~/.ssh/nonproduction_rsa-cert.pub 
 
~/.ssh/nonproduction_rsa-cert.pub:
        Type: ssh-rsa-cert-v01@openssh.com user certificate
        Public key: RSA-CERT 3c:3d:47:...
        Signing CA: RSA 2b:2a:23:...
        Key ID: "username"
        Serial: 12515602213705584981
        Valid: from 2017-02-06T17:03:00 to 2017-03-08T17:04:44
        Principals: 
                username
                admin
        Critical Options: (none)
        Extensions: 
                permit-X11-forwarding
                permit-agent-forwarding
                permit-port-forwarding
                permit-pty
                permit-user-rc
```
