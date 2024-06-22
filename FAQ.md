# Poetry install command freeze at

```
[keyring.backend] Loading KWallet
[keyring.backend] Loading SecretService
[keyring.backend] Loading Windows
[keyring.backend] Loading chainer
[keyring.backend] Loading libsecret
[keyring.backend] Loading macOS
# nothing happens after this, execution is in frozen state
```

Answer
```bash
export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
```


# Some weights of the model checkpoint at LanguageBind were not used

The warning indicate that `transformers` library cannot use downloaded LanguageBind weights. This will affect resulting embeddings.

Answer

The `perf==0.10.0` not suitable for the project. It must be a version after specific commit for unknown reason.
```bash
poetry install 

# or install directly
pip install git+https://github.com/huggingface/peft@08cb3dde577747f6ca6638c884fd66fd16cf2e9d
```