import pytest
import torch

from mbrs.metrics import MetricCOMETkiwi
from mbrs.selectors import Selector

from .rerank import DecoderRerank

SOURCE = "これはテストです"
HYPOTHESES = [
    ["another test", "this is a test", "this is a fest"],
    ["another test", "this is a fest", "this is a test"],
    ["this is a test"],
    ["Producția de zahăr primă va fi exprimată în ceea ce privește zahărul alb;"],
]

BEST_INDICES = [1, 2, 0, 0]
BEST_SENTENCES = [
    "this is a test",
    "this is a test",
    "this is a test",
    "Producția de zahăr primă va fi exprimată în ceea ce privește zahărul alb;",
]
SCORES = torch.Tensor([0.86415, 0.86415, 0.86415, 0.29771])


class TestDecoderRerank:
    def test_decode(self, metric_cometkiwi: MetricCOMETkiwi):
        decoder = DecoderRerank(DecoderRerank.Config(), metric_cometkiwi)
        for i, hyps in enumerate(HYPOTHESES):
            output = decoder.decode(hyps, SOURCE, nbest=1)
            assert output.idx[0] == BEST_INDICES[i]
            assert output.sentence[0] == BEST_SENTENCES[i]
            torch.testing.assert_close(
                torch.tensor(output.score[0]),
                SCORES[i],
                atol=0.0005 / 100,
                rtol=1e-6,
            )

    @pytest.mark.parametrize("nbest", [1, 2])
    def test_decode_selector(
        self, metric_cometkiwi: MetricCOMETkiwi, nbest: int, selector: Selector
    ):
        decoder = DecoderRerank(
            DecoderRerank.Config(), metric_cometkiwi, selector=selector
        )
        for i, hyps in enumerate(HYPOTHESES):
            output = decoder.decode(hyps, SOURCE, nbest=nbest)
            assert len(output.sentence) == min(nbest, len(hyps))
            assert len(output.score) == min(nbest, len(hyps))
