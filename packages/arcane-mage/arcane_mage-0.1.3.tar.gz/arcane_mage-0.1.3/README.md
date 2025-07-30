## Arcane Mage - Automated Fluxnode ArcaneOS Installation

### Introduction

Arcane Mage is a suite of tools designed to ease the installation (and configuration) burden of installing a Fluxnode.

The following is available via the GUI, or CLI:

* Fully automated A to Z Proxmox installs, including Secure Boot key enrollment.
* Mutlicast config broadcast on LANs - fully automated installs, except Secure Boot Key enrollemnt.
* USB stick creation for plug and play automated installs on bare metal

### Configuration Options

See the `examples` directory for sample configurations.

Any option can be easily set via a yaml configuration file, for example, for Proxmox, start on VM creation, rate limits, etc.

It can also reboot direct into `systemd-boot` for systems that allow easy enrollment of keys (usually bare metal systems)

### Installation

Install `uv` - https://docs.astral.sh/uv/getting-started/installation/

To use the default config file `fluxnodes.yaml` in the directory you are in:

```bash
uvx --with arcane_mage python -m arcane_mage
```

Run the following for help:

```bash
uvx -m arcane-mage --help
```

### Hypervisor Setup - Proxmox Automation

In order to use `Arcane Mage` with Proxmox, the following needs to be set up on your hypervisor:

* A user for the API
* An API token (strongly recommended)
* Nginx reverse proxy (strongly recommended)

To set up your Proxmox Instance behind an Nginx reverse proxy, follow these instructions, it doesn't take much effort:

https://pve.proxmox.com/wiki/Web_Interface_Via_Nginx_Proxy

If you don't reverse proxy the api, you can run into connection issues.

To set up your user, go to "Datacenter" on the Proxmox GUI and add a user:

![Proxmox User Page ](proxmox_user.png)

Next, add an api token for your user:

![Proxmox Api Token ](proxmox_user_api_token.png)

Finally, give **BOTH** your user and api token `PVEAdmin` permissions:

![Proxmox Permissions ](proxmox_permissions.png)

You're now good to run Arcane Mage.
