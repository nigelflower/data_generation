from utils import data_generator
from utils.constituent_building import *
from utils.conjugate import *
from utils.randomize import choice
import random
import generation_projects.inductive_biases.person_helper

class MyGenerator(data_generator.InductiveBiasesGenerator):
    def __init__(self):
        super().__init__(uid="relative_position_control",
                         linguistic_feature_type=None,
                         linguistic_feature_description=None,
                         surface_feature_type="relative position",
                         surface_feature_description="Does the word 'the' precede the word 'a'?",
                         control_paradigm=True)

        # match_a = get_matches_of(get_all("expression", "a", all_very_common_dets)[0], "arg_1")
        self.safe_singular_animate_common_nouns = get_matches_of(get_all("expression", "a", all_very_common_dets)[0], "arg_1", all_common_nouns)
        self.safe_dets = np.setdiff1d(np.setdiff1d(all_determiners, get_all("expression", "the")), get_all("expression", "a"))
        self.possibly_singular_cp_verbs = get_all("category", "(S\\NP)/S", all_possibly_singular_verbs)
        self.possibly_singular_transitive_verbs = np.intersect1d(all_transitive_verbs, all_possibly_singular_verbs)

    def sample(self):
        # Training 1/1
        # This man who helped the girl thinks  that that guy found a cat.
        # D1   NP1 rel V1     THE NP2 cp_verb THAT  D3   NP3 V2    A NP4

        # Training 0/0
        # This man who helped A girl thinks  that that guy found the cat.
        # D1   NP1 rel V1     A NP2  cp_verb THAT D3   NP3 V2    THE NP4

        # Test 1/0
        # The  man thinks   that that guy  who helped a girl found every cat.
        # THE  NP1  cp_verb THAT D3   NP3  rel V1     D2 NP2 V2    D4    NP4

        # Test 0/1
        # A   man thinks  that that guy  who helped the girl found every cat.
        # A   NP1  cp_verb THAT D3  NP3  rel V1     THE NP2 V2    D4    NP4


        cp_verb = choice(self.possibly_singular_cp_verbs)
        try:
            NP1 = choice(get_matches_of(cp_verb, "arg_1", self.safe_singular_animate_common_nouns))
        except Exception:
            pass
        D1 = choice(get_matched_by(NP1, "arg_1", self.safe_dets))
        rel1 = choice(get_matched_by(NP1, "arg_1", all_relativizers))
        V1 = choice(get_matched_by(NP1, "arg_1", all_transitive_verbs))
        NP2 = choice(get_matches_of(V1, "arg_2", self.safe_singular_animate_common_nouns))
        D2 = choice(get_matched_by(NP2, "arg_1", self.safe_dets))
        rel2 = choice(get_matched_by(NP2, "arg_1", all_relativizers))
        Aux1 = return_aux(V1, NP1)
        NP3 = choice(get_matches_of(V1, "arg_1", get_matches_of(Aux1, "arg_1", self.safe_singular_animate_common_nouns)))
        D3 = choice(get_matched_by(NP3, "arg_1", self.safe_dets))
        V2 = choice(get_matched_by(NP3, "arg_1", self.possibly_singular_transitive_verbs))
        NP4 = choice(get_matches_of(V2, "arg_2", self.safe_singular_animate_common_nouns))
        D4 = choice(get_matched_by(NP4, "arg_1", self.safe_dets))
        Aux_cp = return_aux(cp_verb, NP1)
        Aux2 = return_aux(V2, NP3)

        Ds = []
        option = random.choice([1, 2, 3])   # There are three in-domain configurations (arbitrarily chosen)
        if option == 1:
            Ds.append(["the", "a", D3[0], D4[0]])
            Ds.append(["a", "the", D3[0], D4[0]])
        elif option == 2:
            Ds.append(["the", D2[0], D3[0], "a"])
            Ds.append(["a", D2[0], D3[0], "the"])
        else:
            Ds.append([D1[0], "the", D3[0], "a"])
            Ds.append([D1[0], "a", D3[0], "the"])

        option = random.choice([1, 2, 3])   # There are three out-domain configurations (arbitrarily chosen)
        if option == 1:
            Ds.append(["the", D3[0], "a", D4[0]])
            Ds.append(["a", D3[0], "the", D4[0]])
        elif option == 2:
            Ds.append([D1[0], "the", "a", D4[0]])
            Ds.append([D1[0], "a", "the", D4[0]])
        else:
            Ds.append([D1[0], D3[0], "the", "a"])
            Ds.append([D1[0], D3[0], "a", "the"])

        track_sentence = [
                (NP1[0], V1[0], NP2[0], cp_verb[0], NP3[0], V2[0], NP4[0]),  #training 1/1
                (NP1[0], V1[0], NP2[0], cp_verb[0], NP3[0], V2[0], NP4[0]),  #training 0/0
                (NP1[0], V1[0], NP2[0], cp_verb[0], NP3[0], V2[0], NP4[0]),  #Test 1/0
                (NP1[0], V1[0], NP2[0], cp_verb[0], NP3[0], V2[0], NP4[0]),  #Test 0/1
            ]

        data = self.build_paradigm(
            training_1_1=" ".join([Ds[0][0], NP1[0], rel1[0], Aux1[0], V1[0], Ds[0][1], NP2[0], Aux_cp[0], cp_verb[0],
                                   "that", Ds[0][2], NP3[0], Aux2[0], V2[0], Ds[0][3], NP4[0]]),
            training_0_0=" ".join([Ds[1][0], NP1[0], rel1[0], Aux1[0], V1[0], Ds[1][1], NP2[0], Aux_cp[0], cp_verb[0],
                                   "that", Ds[1][2], NP3[0], Aux2[0], V2[0], Ds[1][3], NP4[0]]),
            test_1_0=" ".join([Ds[2][0], NP1[0], Aux_cp[0], cp_verb[0], "that", Ds[2][1], NP3[0],
                               rel2[0], Aux1[0], V1[0], Ds[2][2], NP2[0], Aux2[0], V2[0], Ds[2][3], NP4[0]]),
            test_0_1=" ".join([Ds[3][0], NP1[0], Aux_cp[0], cp_verb[0], "that", Ds[3][1], NP3[0],
                               rel2[0], Aux1[0], V1[0], Ds[3][2], NP2[0], Aux2[0], V2[0], Ds[3][3], NP4[0]]),
        )
        return data, track_sentence


generator = MyGenerator()
generator.generate_paradigm(number_to_generate=5000, rel_output_path="outputs/inductive_biases/" + generator.uid)
