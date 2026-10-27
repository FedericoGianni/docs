# Forbay Homelab Docs

Docs use `{{ keys }}`; real values stay in `secrets.local.yml` (not committed),
`secrets.age` is the encrypted copy, and `secrets.scrambled.yml` is the public
fake map.

    make setup
    make unlock     # needs secrets.key
    make serve

    make lock       # regenerate fake values + encrypt
    make publish    # lock + check + commit/push

`secrets.key` is the private key — not commited.
