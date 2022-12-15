import pathlib
import shutil
from datetime import datetime

import yaml

from .gradebook import Gradebook

F_CONFIG_DEFAULT = (pathlib.Path(__file__).parent / 'config.yaml').resolve()


class Config:
    def __init__(self, cat_weight_dict=None, cat_drop_dict=None,
                 remove_list=tuple(), sub_dict=None, waive_dict=None,
                 email_list=None, cat_late_dict=None,
                 exclude_complete_thresh=None,
                 grade_thresh=None):
        self.cat_weight_dict = cat_weight_dict
        self.cat_drop_dict = cat_drop_dict
        self.remove_list = remove_list
        self.sub_dict = sub_dict
        self.waive_dict = waive_dict
        self.email_list = email_list
        self.cat_late_dict = cat_late_dict
        self.exclude_complete_thresh = exclude_complete_thresh
        self.grade_thresh = grade_thresh

    def __call__(self, f_scope):
        """ runs a typical processing pipeline given config and f_scop

        Args:
            f_scope (str): raw gradescope csv

        Returns:
            gradebook (Gradebook): processed gradebook
            df_grade_full (pd.DataFrame): full data frame
        """
        gradebook = Gradebook(f_scope=f_scope)

        if self.email_list is not None:
            gradebook.prune_email(email_list=self.email_list)

        if self.sub_dict is not None:
            gradebook.substitute(sub_dict=self.sub_dict)

        if self.remove_list is not None:
            for ass in self.remove_list:
                gradebook.remove(ass, multi=True)

        if self.exclude_complete_thresh is not None:
            gradebook.remove_thresh(
                min_complete_thresh=self.exclude_complete_thresh)

        if self.waive_dict is not None:
            gradebook.waive(waive_dict=self.waive_dict)

        df_grade_full = gradebook.average_full(
            cat_weight_dict=self.cat_weight_dict,
            cat_drop_dict=self.cat_drop_dict,
            cat_late_dict=self.cat_late_dict,
            grade_thresh=self.grade_thresh)

        return gradebook, df_grade_full

    @classmethod
    def from_file(cls, f_config):
        """ loads config from yaml file

        Args:
            f_config (str): yaml file

        Returns:
            config (Config): configuration
        """
        # load yaml
        with open(f_config, 'r') as f:
            d = yaml.safe_load(f)

        cat_weight_dict = d['category']['weight']
        cat_drop_n = d['category']['drop low']
        cat_late_dict = d['category']['late_penalty']
        exclude_list = d['assignments']['exclude']
        sub_dict = d['assignments']['substitute']
        waive_dict = d['waive']
        email_list = d['email_list']
        exclude_complete_thresh = d['assignments']['exclude_complete_thresh']

        if 'grade_thresh' in d.keys():
            grade_thresh = d['grade_thresh']
        else:
            grade_thresh = None

        return cls(cat_weight_dict, cat_drop_n, exclude_list, sub_dict,
                   waive_dict, email_list, cat_late_dict,
                   exclude_complete_thresh, grade_thresh=grade_thresh)

    @classmethod
    def cli_copy_config(cls, folder):
        """ copies default config file to folder, uses existing local if user wants
        """
        # default config location
        f_config = pathlib.Path(folder) / F_CONFIG_DEFAULT.name

        if f_config.exists():
            # if config already exists, ask if it should be used
            print(f'local config exists: {f_config.resolve()}')
            while True:
                s = input('use [e]xisting config or create [n]ew config?')
                if s == 'e':
                    # use existing config
                    return cls.from_file(f_config)
                elif s == 'n':
                    # create new config
                    s_now = datetime.now().strftime('_%Y_%b_%d@%H:%M:%S')
                    f_config = str(f_config).replace('.yaml', f'{s_now}.yaml')
                    f_config = pathlib.Path(f_config)
                    break
                print('invalid input')

        # copy config
        shutil.copy(F_CONFIG_DEFAULT, f_config)
        print(f'using config file: {f_config}')

        return cls.from_file(f_config)
