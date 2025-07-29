.. _`basic/run`:

Running validations with IMAS-Validator
=======================================

In this section we start with the core functionality of the IMAS-Validator: running tests on IDS data.
The easiest way of using the IMAS-Validator is by using the CLI from your terminal.
The only required argument is the imas_uri of the DBentry object you want to validate.
To print the report output directly to your terminal, add the ``--verbose`` option.

.. code-block:: console

    $ imas_validator validate <DBENTRY_URI>
    $ imas_validator validate <DBENTRY_URI> --verbose

.. note::

  The validator will need to load all data in the supplied data entry. Depending
  on the size of your data entry it may take some time to load this data and
  execute the rules.

You can use the generic tests or custom built validation tests.
We start with the generic tests.

Exercise 1
----------

.. md-tab-set::

    .. md-tab-item:: Exercise

        Run the IMAS-Validator generic tests for the db_entry with uri ``imas:hdf5?path=imas-validator-course/good``

        Run it again with the ``--verbose`` option.

    .. md-tab-item:: Solution

        .. code-block:: console

            $ imas_validator validate 'imas:hdf5?path=imas-validator-course/good'

        The output should be a summary report showing that all tests passed.
        The IDSs tested were core_profiles and waves.

You might want to develop or simply use your own custom tests in addition to the standard
bundled validation tests. You can add customly built tests to the validation process by adding CLI flags
to determine in which ruleset folders the tool should look for IDS validation rules. 
A ruleset is a folder that can contain multiple validation test files, typically grouped per use case.
A rule directory is a folder containing multiple ruleset folders so that the IMAS-Validator can be 
easily told where to look.
The structure of these rulesets folders is further explained in :ref:`defining rules`.
You can find custom rule folders and rulesets with the flags:

- Rule folder (-e, --extra-rule-dirs)
- Ruleset (-r, --ruleset)

.. code-block:: console

    $ imas_validator validate 'imas:hdf5?path=imas-validator-course/good' -e path/to/my_rule_folder -r my_ruleset

Exercise 2
----------

.. md-tab-set::

    .. md-tab-item:: Exercise

        Call the IMAS-Validator including custom tests for the db_entry with uri ``imas:hdf5?path=imas-validator-course/good``.
        The custom rules are defined in the ``imas-validator-training-rulesets/custom_ruleset`` ruleset folder.

    .. md-tab-item:: Solution

        .. code-block:: console

            $ imas_validator validate 'imas:hdf5?path=imas-validator-course/good' -e imas-validator-training-rulesets/ -r custom_ruleset

        More tests should be added to the summary report compared to Exercise 1.
            
Exercise 3
----------

.. md-tab-set::

    .. md-tab-item:: Exercise

        What happens if you run the tests with the ``imas:hdf5?path=imas-validator-course/bad`` uri?

    .. md-tab-item:: Solution

        Failed validation for both IDS instances.
        The summary report should show information for
        `generic/generic.py:validate_increasing_time`
            
.. note::

    The IMAS-Validator tool is also integrated in SimDB

.. note::

    You can also run the IMAS-Validator tool from a python script. This might be helpful if you want to automatically run your
    data through the validation tool after it is measured/generated.
    More information can be found in :ref:`usage`.
