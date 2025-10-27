"""Conversão para TorchScript."""

import argparse
import torch
from pathlib import Path
from dkt_model import load_model


def convert_to_torchscript(model_path, output_path, method="trace"):
    """Converte modelo para TorchScript."""
    model, metadata = load_model(model_path)
    model.eval()

    dummy_input = torch.randint(0, 100, (1, 200))

    if method == "trace":
        traced_model = torch.jit.trace(model, dummy_input)
    elif method == "script":
        traced_model = torch.jit.script(model)
    else:
        raise ValueError(f"Unknown method: {method}")

    traced_model.save(output_path)
    print(f"✓ Modelo convertido para {output_path}")

    # Teste
    with torch.no_grad():
        out1 = model(dummy_input)
        out2 = traced_model(dummy_input)
        diff = torch.abs(out1 - out2).max().item()
        print(f"Max difference: {diff}")
        assert diff < 1e-5, "Conversion failed"

    return traced_model


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="models/dkt.pt")
    parser.add_argument("--output", default="models/dkt_ts.pt")
    parser.add_argument("--method", default="trace", choices=["trace", "script"])
    args = parser.parse_args()

    convert_to_torchscript(args.model, args.output, args.method)
