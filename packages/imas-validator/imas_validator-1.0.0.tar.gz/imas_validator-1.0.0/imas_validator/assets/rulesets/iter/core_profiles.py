"""ITER-specific validation rules for the ``core_profiles`` IDS."""

@validator("core_profiles")
def validate_global_quantities_ip(ids):
    """Validate that -17 MA <= global_quantities.ip <= 0"""

    assert -17000000.0 <= ids.global_quantities.ip <= 0.0


@validator("core_profiles")
def validate_profiles_1d_q(ids):
    """Validate that profiles_1d.q > 0"""

    for profiles_1d in ids.profiles_1d:
        assert 0.0 < profiles_1d.q
