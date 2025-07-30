from contextlib import nullcontext
from datetime import datetime, timedelta, timezone

from numpy import around
from pytest import approx, mark, raises
from shapely import LineString, Point, Polygon, is_ccw
from shapely.geometry import mapping, shape

from tle_sat.satellite import (
    FieldOfView,
    FootprintError,
    Pass,
    Satellite,
    TimeOfInterest,
    ViewAngles,
)


def _assert_pass_equals(p1: Pass, p2: Pass):
    p1l = [
        p1.view_angles.across,
        p1.view_angles.along,
        p1.view_angles.off_nadir,
        p1.azimuth,
        p1.incidence,
        p1.sun_azimuth,
        p1.sun_elevation,
    ]
    p2l = [
        p2.view_angles.across,
        p2.view_angles.along,
        p2.view_angles.off_nadir,
        p2.azimuth,
        p2.incidence,
        p2.sun_azimuth,
        p2.sun_elevation,
    ]
    assert p1l == approx(p2l)


def _precision(geom: Polygon | LineString, precision=6):
    geojson = mapping(geom)
    geojson["coordinates"] = around(geojson["coordinates"], precision)
    return shape(geojson)


def test_position_invalid_datetime(polar_tle):
    sat = Satellite(polar_tle)
    t = datetime(2024, 4, 19, 12, 0, 0, 0)

    with raises(ValueError, match="datetime must be in utc"):
        sat.position(t)


@mark.parametrize(
    "t, p",
    (
        (
            datetime(2024, 4, 19, 12, 0, 0, 0, timezone.utc),
            Point(152.6226382884999, 78.18538506762289, 557934.9901695348),
        ),
    ),
)
def test_position(polar_tle, t, p):
    sat = Satellite(polar_tle)

    pos = sat.position(t)

    assert pos.equals(p)


@mark.parametrize(
    "t,o,v",
    (
        (
            datetime(2024, 4, 19, 12, 0, 0, 0, timezone.utc),
            [-5, 0, 0],
            ViewAngles(-0.3, -11.5, 11.555752058027988),
        ),
        (
            datetime(2024, 4, 19, 12, 0, 0, 0, timezone.utc),
            [5, 0, 0],
            ViewAngles(-0.7, 11.5, 11.555752058027988),
        ),
    ),
)
def test_view_angles(polar_tle, t, o, v):
    sat = Satellite(polar_tle)
    p = sat.position(t)

    on = sat.view_angles(t, Point(p.x + o[0], p.y + o[1], o[2]))

    assert on.across == approx(v.across, abs=0.1)
    assert on.along == approx(v.along, abs=0.1)
    assert on.off_nadir == approx(v.off_nadir, abs=0.1)


@mark.parametrize(
    "t, v, f, expectation",
    (
        (
            datetime(2024, 4, 19, 12, 0, 0, 0, timezone.utc),
            ViewAngles(0, 45, 45),
            FieldOfView(2, 2),
            nullcontext(
                Polygon(
                    (
                        (175.60359680143947, 76.98714113663245),
                        (177.22394652541345, 76.81734966236745),
                        (177.71903131823174, 77.05665979118999),
                        (176.05545933500957, 77.21951692944646),
                        (175.60359680143947, 76.98714113663245),
                    )
                )
            ),
        ),
        (
            datetime(2024, 4, 19, 12, 0, 0, 0, timezone.utc),
            ViewAngles(0, 90, 45),
            FieldOfView(2, 2),
            raises(FootprintError, match="footprint not fully on earth"),
        ),
    ),
)
def test_footprint(polar_tle, t, v, f, expectation):
    sat = Satellite(polar_tle)

    with expectation as e:
        footprint = sat.footprint(t, v, f)
        assert _precision(e, 8).equals(_precision(footprint, 8))

        if isinstance(e, Polygon):
            assert is_ccw(footprint.exterior)
            assert all(not is_ccw(interior) for interior in e.interiors)


@mark.parametrize(
    "target,t,footprint",
    (
        (
            Point(13, 53, 0),
            datetime(2024, 4, 19, 21, 39, 59, tzinfo=timezone.utc),
            Polygon(
                (
                    (13.20496447259038, 52.87415752284107),
                    (12.758567800131482, 52.90986652401911),
                    (12.799711072078717, 53.12031287404936),
                    (13.249444062185855, 53.090245713914435),
                    (13.20496447259038, 52.87415752284107),
                )
            ),
        ),
    ),
)
def test_pass_footprint(polar_tle, target: Point, t: datetime, footprint: Polygon):
    sat = Satellite(polar_tle)

    passes = sat.passes(
        TimeOfInterest(t - timedelta(minutes=15), t + timedelta(minutes=15)), target
    )
    assert len(passes) == 1
    p = passes[0]

    actual_footprint = sat.footprint(t=p.t, view_angles=p.view_angles)

    assert _precision(footprint, 8).equals(_precision(actual_footprint, 8))
    assert actual_footprint.contains(target)
    assert _precision(footprint.centroid, 2).equals(_precision(target, 2))


@mark.parametrize(
    "t,target,passes",
    (
        (
            datetime(2024, 4, 19, 12, 0, 0, 0, timezone.utc),
            Point(151.6226382884999, 78.18538506762289, 0),
            [
                Pass(
                    t=datetime(2024, 4, 19, 10, 24, 10, 13017, tzinfo=timezone.utc),
                    view_angles=ViewAngles(
                        along=0.003286938613857222,
                        across=-43.59378581863903,
                        off_nadir=43.59378587058238,
                    ),
                    azimuth=246.15947980920845,
                    incidence=48.56258642963941,
                    sun_azimuth=309.1665849748783,
                    sun_elevation=4.040713411924881,
                ),
                Pass(
                    t=datetime(2024, 4, 19, 12, 0, 0, 14, tzinfo=timezone.utc),
                    view_angles=ViewAngles(
                        along=0.012069782991351924,
                        across=-2.3465815282339757,
                        off_nadir=2.3466124994902096,
                    ),
                    azimuth=269.51084026095725,
                    incidence=2.5513557385532977,
                    sun_azimuth=332.4719846650721,
                    sun_elevation=0.9843777205236294,
                ),
                Pass(
                    t=datetime(2024, 4, 19, 13, 35, 18, 176643, tzinfo=timezone.utc),
                    view_angles=ViewAngles(
                        along=0.036206722030285,
                        across=41.38571967607966,
                        off_nadir=41.38572698419228,
                    ),
                    azimuth=113.21914991193279,
                    incidence=45.954108011810156,
                    sun_azimuth=355.78438524781876,
                    sun_elevation=-0.318769078583524,
                ),
            ],
        ),
    ),
)
def test_passes(polar_tle, t, target, passes):
    sat = Satellite(polar_tle)

    calculated = sat.passes(
        TimeOfInterest(t - timedelta(hours=2), t + timedelta(hours=2)),
        target,
    )

    for p1, p2 in zip(calculated, passes):
        _assert_pass_equals(p1, p2)


@mark.parametrize(
    "kwargs,track",
    (
        (
            {
                "toi": TimeOfInterest(
                    datetime(2024, 10, 15, 12, 0, 0, 0, timezone.utc),
                    datetime(2024, 10, 15, 12, 0, 10, 0, timezone.utc),
                )
            },
            LineString(
                (
                    [156.19155330523242, -79.17285283352071, 567798.5875704342],
                    [156.1873752306572, -79.1105217749056, 567788.6547832417],
                    [156.1831971560807, -79.04819034745724, 567778.6756299192],
                    [156.17901908150557, -78.98585854951246, 567768.650148406],
                    [156.17484100692906, -78.92352637940978, 567758.5783768552],
                    [156.17066293235393, -78.86119383466138, 567748.4603534729],
                    [156.1664848577762, -78.79886091402265, 567738.2961168538],
                    [156.16230678320102, -78.73652761562968, 567728.0857057112],
                    [156.15812870862462, -78.6741939369995, 567717.8291588447],
                    [156.1539506340468, -78.61185987689188, 567707.5265154454],
                    [156.14977255947426, -78.54952543344785, 567697.1778148033],
                )
            ),
        ),
        (
            {
                "toi": TimeOfInterest(
                    datetime(2024, 10, 15, 12, 0, 0, 0, timezone.utc),
                    datetime(2024, 10, 15, 12, 1, 0, 0, timezone.utc),
                ),
                "step": 10,
            },
            LineString(
                (
                    [156.19155330523242, -79.17285283352071, 567798.5875704342],
                    [156.14977255947426, -78.54952543344785, 567697.1778148033],
                    [156.1079918137122, -77.92615949416424, 567591.16644218],
                    [156.0662110679566, -77.3027531680104, 567480.5940142936],
                    [156.02443032219713, -76.67930462151435, 567365.5030351874],
                    [155.98264957644153, -76.05581204157784, 567245.9379344286],
                    [155.94086883068337, -75.43227363068695, 567121.9450473494],
                )
            ),
        ),
    ),
)
def test_orbit_track(polar_tle, kwargs, track):
    sat = Satellite(polar_tle)

    calculated = sat.orbit_track(**kwargs)
    assert _precision(calculated, 7) == _precision(track, 7)


@mark.parametrize(
    "kwargs,swath",
    (
        (
            {
                "toi": TimeOfInterest(
                    datetime(2024, 10, 15, 12, 0, 0, 0, timezone.utc),
                    datetime(2024, 10, 15, 12, 0, 10, 0, timezone.utc),
                ),
                "fov": FieldOfView(2, 2),
            },
            Polygon(
                (
                    (156.6737515792948, -79.26013698492129),
                    (156.57850629939526, -79.26048755802557),
                    (156.4832657999816, -79.26081028731663),
                    (156.38802791844955, -79.26110518749252),
                    (156.29279049245753, -79.26137227033419),
                    (156.19755135973534, -79.26161154470728),
                    (156.1023083578922, -79.26182301656365),
                    (156.0070593242257, -79.26200668894188),
                    (155.9118020955298, -79.26216256196727),
                    (155.81653450790324, -79.2622906328512),
                    (155.72125439655778, -79.26239089588978),
                    (155.71912004959748, -79.17361126882491),
                    (155.71762170565935, -79.11128866663313),
                    (155.7160927268066, -79.04896567023418),
                    (155.71453363283865, -78.98664227835933),
                    (155.712944931854, -78.92431848973247),
                    (155.7113271206227, -78.86199430224252),
                    (155.70968068480434, -78.79966971501283),
                    (155.70800609934696, -78.73734472653913),
                    (155.70630382876317, -78.67501933469022),
                    (155.7045743273543, -78.61269353856947),
                    (155.70281803956516, -78.55036733665398),
                    (155.7002989674138, -78.46159986199008),
                    (155.78903247066273, -78.46149190992259),
                    (155.877754245772, -78.46135584928601),
                    (155.96646631780737, -78.46119168532044),
                    (156.0551707109901, -78.4609994204004),
                    (156.14386944888085, -78.46077905403604),
                    (156.23256455456334, -78.4605305828738),
                    (156.3212580508279, -78.46025400069634),
                    (156.40995196035462, -78.4599492984219),
                    (156.4986483058975, -78.45961646410294),
                    (156.5873491104672, -78.45925548292418),
                    (156.59663613701923, -78.548005082268),
                    (156.60323548360986, -78.61034393102136),
                    (156.60986161101897, -78.67268237734349),
                    (156.61651496358516, -78.7350204227399),
                    (156.62319599551603, -78.7973580680897),
                    (156.6299051712349, -78.85969531550688),
                    (156.6366429655807, -78.92203216647829),
                    (156.64340986412017, -78.98436862186304),
                    (156.65020636351423, -79.04670468375495),
                    (156.65703297176154, -79.10904035341271),
                    (156.66389020854774, -79.1713756320875),
                    (156.6737515792948, -79.26013698492129),
                ),
            ),
        ),
        (
            {
                "toi": TimeOfInterest(
                    datetime(2024, 10, 15, 12, 0, 0, 0, timezone.utc),
                    datetime(2024, 10, 15, 12, 1, 0, 0, timezone.utc),
                ),
                "fov": FieldOfView(2, 2),
                "step": 10,
                "steps_across": 3,
            },
            Polygon(
                (
                    (156.6737515792948, -79.26013698492129),
                    (156.35628216594836, -79.26119730542355),
                    (156.03880980583594, -79.26194855357903),
                    (155.72125439655778, -79.26239089588978),
                    (155.71912004959748, -79.17361126882491),
                    (155.70281803956516, -78.55036733665398),
                    (155.68387312768436, -77.92708264629658),
                    (155.66267432728918, -77.30375564318372),
                    (155.6395378619908, -76.68038473051257),
                    (155.61472342871872, -76.05696828805078),
                    (155.58844628724063, -75.4335046767285),
                    (155.58461969170088, -75.34480954527784),
                    (155.8182003662874, -75.34406502833157),
                    (156.05171728652488, -75.34307434748894),
                    (156.28523447863842, -75.34183724754735),
                    (156.29322064492862, -75.43051475045617),
                    (156.35050166028583, -76.0541031166526),
                    (156.4092450795197, -76.67764472084889),
                    (156.4696661176312, -77.30114118505205),
                    (156.53202441751313, -77.92459411233826),
                    (156.59663613701923, -78.548005082268),
                    (156.66389020854774, -79.1713756320875),
                    (156.6737515792948, -79.26013698492129),
                )
            ),
        ),
    ),
)
def test_swath(polar_tle, kwargs, swath):
    sat = Satellite(polar_tle)

    calculated = sat.swath(**kwargs)
    assert _precision(calculated, 8) == _precision(swath, 8)
