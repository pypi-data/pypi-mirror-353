from anonypyx.attackers.util import split_columns
from anonypyx.attackers.base_attacker import BaseAttacker, parse_prior_knowledge


class CrackSizes:
    def __init__(self, sensitive_values, timestamp):
        self._timestamp = timestamp
        self._sensitive_values = sensitive_values

    def update(self, sensitive_values, timestamp):
        for sensitive_value, group_size in self._sensitive_values.items():
            pass


    def _forward_attack(self, old_group_size, new_group_size):
        return old_group_size - min(old_group_size, new_group_size)

    def _cross_attack(self, old_group_size, new_group_size):
        return new_group_size - min(old_group_size, new_group_size)

    # keep a set for every target
    # for the F and C attacks, it suffices to store the minimum group size and use it for the attack
    # the choice of "cracking" and "background release" remains unclear for the time being...
    # the B attack is also complex: this zig-zag matching between two releases requires access to all releases during the micro-attacks, doesn't it?
    # yeah, the B attack on multiple releases is a complete mess: if the target is inserted at time j, the attacker must consider all releases i < j and examine the mutual correspondence/compatability relation between the target's EC in release j and the ECs of the previous releases (and back to the ECs of release j again...) thus if there are multiple targets added in different releases, the adversary must pretty much consider all possible overlaps between the released ECs... Also, the adversary must have access to everything at the same time, you can hardly preprocess anything because the EC/generalised QI is only revealed in release j
    # maybe use a bit different approach here: the attacker attacks precisely one target

class BCFAttacker(BaseAttacker):
    def __init__(self, prior_knowledge, quasi_identifiers, sensitive_column, schema):
        '''
        Constructor.

        Parameters
        ----------
        prior_knowledge : pandas.DataFrame
            A data frame containing the attacker's prior knowledge about their targets. It must use the
            same generalisation schema as the data frames the attacker will observe() (minus the column
            'count'). Furthermore, it must contain a column 'ID' which uniquely identifies every target.
            The ID must start at zero and increase strictly monotonically (i.e. IDs must be 0, 1, ...,
            num_targets - 1). The data frame may contain multiple rows with the same ID which is
            interpreted as an attacker having alternative hypotheses about the target. At least one
            hypothesis (row) for every ID must be true.
        quasi_identifiers : list of str
            The names of the columns in the original data frames (before generalisation) which act as
            quasi-identifiers (i.e. those for which the attacker knows the exact values).
        sensitive_column : str
            The names of the column in the original data frames (before generalisation) which acts as
            the sensitive attribute (i.e. the one the attacker attempts to reconstruct).
        schema : anonypyx.generalisation.GeneralisedSchema
            The generalisation schema used by the data frames the attacker will observe() and by
            prior_knowledge.
        '''
        self._candidates = []

        def id_callback(target_id, target_knowledge):
            for _, row in target_knowledge.iterrows():
                # TODO: only one row per target supported right now
                self._candidates.append(SensitiveValueSet(row, quasi_identifiers, sensitive_column, schema))

        # TODO: use column name 'ID' instead of fixed position
        num_targets = parse_prior_knowledge(prior_knowledge, id_callback)

    def observe(self, release, present_columns, present_targets):
        for target_id in present_targets:
            self._candidates[target_id].update(release)

    def predict(self, target_id, column):
        return self._candidates[target_id].values_for(column)
