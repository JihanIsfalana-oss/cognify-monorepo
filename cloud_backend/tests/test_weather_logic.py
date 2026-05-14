# cloud_backend/tests/test_weather_logic.py

import math
import pytest
from app.services.weather_service import calculate_et0_simple


class TestET0Formula:
    """
    Validasi formula ET0 Hargreaves (FAO-56 Allen et al. 1998).
    Nilai referensi diambil dari FAO Irrigation Paper 56, Appendix 2.
    """

    def test_et0_positive_for_tropical_conditions(self):
        """Kondisi tropis Indramayu: suhu tinggi, range suhu sedang."""
        et0 = calculate_et0_simple(
            temp_mean=29.5,
            temp_max=33.0,
            temp_min=24.0,
            day_of_year=180,
            latitude_rad=math.radians(-6.32)   # Indramayu
        )
        assert et0 > 0, "ET0 harus positif"

    def test_et0_in_realistic_range_tropics(self):
        """ET0 tropis harus antara 3-12 mm/hari (range realistis FAO-56)."""
        et0 = calculate_et0_simple(
            temp_mean=29.5,
            temp_max=33.0,
            temp_min=24.0,
            day_of_year=180,
            latitude_rad=math.radians(-6.32)
        )
        assert 3.0 <= et0 <= 12.0, (
        f"ET0 {et0} mm/hari di luar range realistis tropik (3-12 mm/hari). "
        f"Referensi: FAO Irrigation Paper 56, Allen et al. 1998, Appendix 2."
        )
    def test_higher_temp_range_increases_et0(self):
        """Selisih suhu lebih besar → ET0 lebih tinggi (efek √(Tmax-Tmin))."""
        et0_narrow = calculate_et0_simple(29.5, 31.0, 28.0, 180, math.radians(-6.32))
        et0_wide   = calculate_et0_simple(29.5, 36.0, 23.0, 180, math.radians(-6.32))
        assert et0_wide > et0_narrow

    def test_et0_at_equinox_vs_solstice(self):
        """Ra berbeda di ekuinoks (doy=80) vs solstice (doy=172) — ET0 harus berbeda."""
        et0_equinox  = calculate_et0_simple(29.5, 33.0, 24.0, 80,  math.radians(-6.32))
        et0_solstice = calculate_et0_simple(29.5, 33.0, 24.0, 172, math.radians(-6.32))
        assert et0_equinox != pytest.approx(et0_solstice, abs=0.1)

    def test_zero_temp_range_raises_or_returns_zero(self):
        """Tmax == Tmin → √0 = 0 → ET0 harus 0."""
        et0 = calculate_et0_simple(29.5, 29.5, 29.5, 180, math.radians(-6.32))
        assert et0 == pytest.approx(0.0, abs=0.001)

    def test_return_type_is_float(self):
        et0 = calculate_et0_simple(29.5, 33.0, 24.0, 180, math.radians(-6.32))
        assert isinstance(et0, float)

    def test_result_rounded_to_2_decimal(self):
        et0 = calculate_et0_simple(29.5, 33.0, 24.0, 180, math.radians(-6.32))
        assert et0 == round(et0, 2)