from utils import data_generator
from utils.conjugate import *
from utils.constituent_building import *
from utils.conjugate import *
from utils.randomize import choice
from utils.string_utils import string_beautify
from functools import reduce
from utils.vocab_sets import *


class AgreementGenerator(data_generator.BenchmarkGenerator):
    def __init__(self):
        super().__init__(field="morphology",
                         linguistics="subject_verb_agreement",
                         uid="irregular_plural_subject_verb_agreement_1",
                         simple_lm_method=True,
                         one_prefix_method=True,
                         two_prefix_method=False,
                         lexically_identical=False)
        self.safe_nouns = get_all_conjunctive([("category", "N"), ("irrpl", "1"), ("sgequalspl", "")])
        # self.safe_nouns = np.array(filter(lambda x: x["pluralform"] != x["expression"], all_irreg_nouns), dtype=data_type)
        self.safe_verbs = reduce(np.union1d, (get_all("pres", "1", all_verbs),
                                              get_all("ing", "1", all_verbs),
                                              get_all("en", "1", all_verbs)))

    def sample(self):
        # The cat is        eating food
        #     N1  aux_agree V1     N2
        # The cat are          eating food
        #     N1  aux_nonagree V1     N2

        N1 = N_to_DP_mutate(choice(self.safe_nouns))
        V1 = choice(get_matched_by(N1, "arg_1", self.safe_verbs))
        VP = V_to_VP_mutate(V1, aux=False)
        auxes = require_aux_agree(V1, N1)
        aux_agree = auxes["aux_agree"]
        aux_nonagree = auxes["aux_nonagree"]

        data = {
            "sentence_good": "%s %s %s." % (N1[0], aux_agree, VP[0]),
            "sentence_bad": "%s %s %s." % (N1[0], aux_nonagree, VP[0]),
            "one_prefix_prefix": "%s" % (N1[0]),
            "one_prefix_word_good": aux_agree,
            "one_prefix_word_bad": aux_nonagree
        }
        return data, data["sentence_good"]

generator = AgreementGenerator()
generator.generate_paradigm(rel_output_path="outputs/benchmark/%s.jsonl" % generator.uid, number_to_generate=10)
