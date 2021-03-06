#!/usr/bin/env python3
import unittest
from make_GenePS import *
import re


script_path = os.path.dirname(os.path.realpath(__file__))
test_data = os.path.join(script_path, "test_data")
single_file = os.path.join(test_data, "group1/eef_test.fa")
file_name = "eef_test"


class TestWalkThroughInput(unittest.TestCase):

    dir_tree = walk_through_input(test_data)
    file_tree = walk_through_input(single_file)
    single_folder = walk_through_input(os.path.join(test_data, "group1"))

    def test_input_is_file(self):
        for path, file in self.file_tree.items():
            file_path = os.path.join(path, file[0])
            self.assertTrue(file_path == single_file)

    def test_number_of_groups(self):
        self.assertTrue(len(self.dir_tree), 2)

    def test_number_of_file(self):
        num_files = 0
        for folder, file_list in self.dir_tree.items():
            num_files += len(file_list)
        self.assertEqual(num_files, 10)

    def test_folder_name(self):
        for folder in self.dir_tree.keys():
            folder = folder.split("/")[-1]
            self.assertIn(folder, ["group1", "group2", "test_data"])

    def test_file_name_true(self):
        kog_file = self.dir_tree[os.path.join(test_data, "group2")][0]
        self.assertRegex(kog_file, "KOG0018.fas")


class TestHashFasta(unittest.TestCase):

    fa_hash = hash_fasta(single_file)

    def test_correct_header(self):
        self.assertIn('>ASUUM1.ASU_00947', self.fa_hash.keys())

    def test_correct_sequence(self):
        seq_list = [x[0] for x in self.fa_hash.values()]
        for seq in seq_list:
            self.assertNotIn(">", seq)

    def test_equal_number_header_seq(self):
        number_seq = len(self.fa_hash.keys())
        number_header = len(self.fa_hash.values())
        self.assertEqual(number_header, number_seq)

    def test_number_of_entries(self):
        number_entries = len(self.fa_hash.keys())
        self.assertEqual(number_entries, 11)

    def test_correct_seq_length(self):
        single_seq = len(self.fa_hash[">AMELL.GB42352-PA"][0])
        self.assertEqual(single_seq, 942)


class TestMsaObject(unittest.TestCase):

    msa_list = generate_msa(single_file)
    out_dir = os.path.join(test_data, "group1")

    def test_generate_msa(self):
        self.assertEqual((len(self.msa_list)/2), 11)

    def test_msa_obj_type(self):
        with tempdir() as tmp_dir:
            msa_obj = MsaObject(self.msa_list, file_name, tmp_dir)
            self.assertTrue(type(msa_obj) == MsaObject)

    def test_msa_path(self):
        with tempdir() as tmp_dir:
            msa_obj = MsaObject(self.msa_list, file_name, tmp_dir)
            self.assertTrue(msa_obj.path == os.path.join(tmp_dir, "eef_test.msaGenePS"))

    def test_trim_remove(self):
        with tempdir() as tmp_dir:
            msa_obj = MsaObject(self.msa_list, file_name, tmp_dir)
            msa_obj.msa_to_fasta()
            msa_obj.trim_remove()
            org_size, trim_size = msa_obj.size[0], msa_obj.size[1]
            self.assertEqual(int((org_size - trim_size)), 5)

    def test_trim_length(self):
        with tempdir() as tmp_dir:
            msa_obj = MsaObject(self.msa_list, file_name, tmp_dir)
            msa_obj.msa_to_fasta()
            msa_obj.trim_length()
            org_len, trim_len = msa_obj.lengths[0], msa_obj.lengths[1]
            self.assertEqual(int((org_len - trim_len)), 372)

    def test_all_header(self):
        with tempdir() as tmp_dir:
            msa_obj = MsaObject(self.msa_list, file_name, tmp_dir)
            msa_obj.msa_to_fasta()
            header_list = msa_obj.all_header()
            for header in header_list:
                self.assertIn(">", header)

    def test_all_aln(self):
        with tempdir() as tmp_dir:
            msa_obj = MsaObject(self.msa_list, file_name, tmp_dir)
            msa_obj.msa_to_fasta()
            seq_list = msa_obj.all_aln()
            regex = re.compile('[^a-zA-Z]')
            for seq in seq_list:
                seq = seq.replace("-", "")
                self.assertFalse(re.match(regex, seq))


class TestScoreObject(unittest.TestCase):

    fa_hash = hash_fasta(single_file)
    msa_list = generate_msa(single_file)
    eef_scores = [1981, 1808, 1893, 1981, 1981, 1889]
    left_taxa = ['>MINCO1.Minc01141 850 bp', '>PREDI.g17259.t1 850 bp',
                 '>PJUL7.cds.JU765comp10941_c0_seq1m.15227 850 bp', '>MINCO2.g11856.t1 850 bp',
                 '>MJAVA.g3839.t1 850 bp', '>ASUUM1.ASU_00947 850 bp']
    test_consensus = "MVNFTVDEIRALMDKKKNIRNMSVIAHVDHGKSTLTDSLVSKAGIIAGAKAGETRFTDTRKDEQDRCITIKSTAISLFFELD" \
                     "EKDLDFVKGDNQIDIVDGAKKKYNGFLINLIDSPGHVDFSSEVTAALRVTDGALVVVDCVSGVCVQTETVLRQAIAERIKPV" \
                     "LFMNKMDRALLELQLGQEELYQTFQRIVENINVIIATYGDDDGPMGAIQVDPAIGNVGFGSGLHGWAFTLKQFAEMYADKFG" \
                     "VQVDKLMKNLWGDRFFNLKTKKWTSTQEDDTKRGFVQFVLDPIFKVFDAVMNVKKEETTKLVEKLNVKLAAEEKDLEGKALL" \
                     "KVLMRKWLPAGDTMLQMICIHLPSPVTAQKYRMEMLYEGPHDDEAAIAIKACDPNGPLMMYISKMVPTSDKGRFYAFGRVFS" \
                     "GKVATGMKARIQGPNYVVGKKEDLYEKTIQRTILMMGRYIEPIEDIPAGNIAGLVGVDQYLVKGGTITTFKDAHNLRVMKFS" \
                     "VSPVVRVAVEPKNAGDLPKLVEGLKRLAKSDPMVQCIFEESGEHIIAGAGELHLEICLKDLEEDHACIPIKKSDPVVSYRET" \
                     "VTEESDIMCLSKSPNKHNRLFCKAKPLADGLAEAIEKGEVSARDEAKNRAKILAEKYEFDATDARKIWCFGPDGTGANLLVD" \
                     "VTKGVQYLNEIKDSVVAGFQWATKEGVLCDENLRGVRFDIHDVTLHADAIHRGGGQIIPTARRVLYASVLTAKPRLLEPVYL" \
                     "VEIQCPEAAVGGIYGVLNRRRGVVFEESQIAGTPMFIVKAYLPVNESFGFTADLRSNTGGQAFPQCVFDHWQILPGDPLEST" \
                     "SKPAQVVAETRKRKGLKEGIPALDNFLDKL"

    def test_obj_name(self):
        with tempdir() as tmp_dir:
            scoring_obj = ScoreObject(self.fa_hash, self.left_taxa, file_name, tmp_dir)
            self.assertTrue(scoring_obj.name == file_name + ".hmmGenePS")

    def test_phmm_path_not_none(self):
        with tempdir() as tmp_dir:
            scoring_obj = ScoreObject(self.fa_hash, self.left_taxa, file_name, tmp_dir)
            self.assertFalse(scoring_obj.hmm_path)
            scoring_obj.compute_full_phmm()
            self.assertTrue(scoring_obj.hmm_path)

    def test_correct_score_list(self):
        with tempdir() as tmp_dir:
            scoring_obj = ScoreObject(self.fa_hash, self.left_taxa, file_name, tmp_dir)
            score_list = scoring_obj.compute_scores()
            self.assertListEqual(score_list, self.eef_scores)

    def test_query_to_fasta(self):
        with tempdir() as tmp_dir:
            scoring_obj = ScoreObject(self.fa_hash, self.left_taxa, file_name, tmp_dir)
            fasta_string = scoring_obj.query_for_fasta(">MINCO1.Minc01141 850 bp")
            control = ">MINCO1.Minc01141" + "\n" + "".join(self.fa_hash[">MINCO1.Minc01141"])
            self.assertTrue(fasta_string == control)

    def test_get_consensus(self):
        with tempdir() as tmp_dir:
            cons_hmm = os.path.join(tmp_dir, file_name + ".chmm")
            msa_obj = MsaObject(self.msa_list, file_name, tmp_dir)
            msa_obj.msa_to_fasta()
            msa_obj.trim_remove()
            msa_obj.trim_length()
            generate_hmm(cons_hmm, msa_obj.path)
            consensus_seq = get_consensus(cons_hmm)
            self.assertTrue(consensus_seq == self.test_consensus)


if __name__ == '__main__':
    unittest.main()


