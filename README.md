# Komrade

Komrade is a socialist network. It seizes the means of content production.

## Why another social network?

Is a 'socialist network' possible? Although the internet began with anarchic design principles, it quickly consolidated into the hands of a few of the largest corporations in the world. It has effectively recreated the capitalist mode of production within itself: the means of content production (social media platforms) are privatized while the work of production (posting) remains socially distributed. Exploitation inheres in that relation, whether in the industrial factory or the digital platform, because the value you produce is taken from you, concentrated and privatized.

But a digital network can be redesigned. The technology behind these social media platforms is actually quite simple. We can easily build our own social network, one which is secure, insurveillable, and unmonetizable—one which would give people the security they need to communicate about whatever they want, including protesting against capital and the state.

Social networks are weightless. They should be easy to communize.

## Core principles

### Encrypted

All of your data is strongly encrypted, and only you and those you choose will be able to decrypt and read it. To anyone without the right decryption 'key', the data is nonsense.

### Decentralized

Komrade doesn't live on a server, but rather in the ether between all the devices curently running Komrade. Rather than the hierarchical server/client relationship, which exposes the entire network to attacks on a central server, and expose the anonymity on both parties, Komrade uses peer-to-peer networking to 'flood' encrypted data across the network.

### Anonymous

It's impossible to tell who or sent what to anyone. All peers in the network share data randomly, but only the intended recipients have the right decryption key to unlock it. This is a different kind  of cloud: a 'dust cloud' of strongly encrypted information. Ideally, for extra anonymity, all network traffic will be routed through Tor (a global maze of computers which hides your footprints), though this currently faces some serious technical challenges.

### Unmonetizable

What's untraceable is also unmonetizable: your data can't be harvested by technology companies and used for advertising algorithms. You're protected from both surveillance capitalism and the surveillance state.

### Open-source

Not just non-profit, we're anti-profit. 

## Social media features

We present a simplified set of social media features drawn from everything that's out there and then some:

#### Profile
  * Curate a profile with photo and posts (e.g. Twitter)
  * Show profile to world (e.g. Twitter)
  * Show profile only to friends (e.g. Facebook)
  * Show profile only to your local area (e.g. Nextdoor)

#### Posting
  * Post up to 1 image and/or 1000 characters
  * Post to the entire world (e.g. Twitter)
  * Post to your friends (e.g. Facebook)
  * Post to your surrounding area by a distance radius (e.g. Nextdoor)
  * Anonymously up-vote or down-vote posts (e.g. Reddit)
  * Post anonymously or from your account (new)

#### Organizing
  * Host events and invite others (e.g. Facebook)
  * Host events like protests anonymously (new)
  * Anonymously pin on a map sites of danger, like police (e.g. Waze)

#### Messaging
  * Message securely with encrypted contents (e.g. Signal)
  * Message securely with untraceable metadata (new)


## Progress


### Preview animation

As of the 23rd of August.

<img src="app/assets/komrade-screen-preview-2020-08-23.gif" height="600" alt="GIF animation" />


## Technical details

Design details are changing rapidly, but these are what we have so far.

### App

The cross-platform app is made with [KivyMD](https://github.com/kivymd/KivyMD), a variant of [Kivy](https://kivy.org/), a cross-platform mobile development framework in Python. Python is an easy and versatile progamming language to learn, which keeps the code accessible to as many people as possible.

### Database

The database is a [Kademlia](https://github.com/bmuller/kademlia) Distributed Hash Table, a p2p data store, written in Python.

## Install

### As developer

The usual installation:

```
git clone https://github.com/quadrismegistus/Komrade.git
cd Komrade
pip install -r requirements.txt
```

Then run the client:
```
cd client
./run.sh
```


### As user

Coming soon. 