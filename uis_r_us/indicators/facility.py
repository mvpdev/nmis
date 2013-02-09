def _sector_slugs():
    return {
          "water": [
            [
              "Developed/treated spring and surface water",
              "num_developed_and_treated_or_protected_surface_or_spring_water"
            ],
            [
              "Protected dug wells",
              "num_protected_dug_wells"
            ],
            [
              "Boreholes and tube wells",
              "num_boreholes_and_tubewells"
            ],
            [
              "Boreholes and tube wells with non-motorized lift/pump mechanisms",
              "num_boreholes_tubewells_manual"
            ],
            [
              "Boreholes and tube wells with motorized lift/pump mechanisms",
              "num_boreholes_tubewells_non_manual"
            ],
            [
              "Well-maintained boreholes, protected and treated water sources",
              "num_protected_water_sources_functional"
            ],
            [
              "Population served per well-maintained borehole, protected or treated water source",
              "population_served_per_protected_and_functional_water_source"
            ]
          ],
          "education": [
            [
              "Preprimary",
              "num_preprimary_level"
            ],
            [
              "Preprimary and primary",
              "num_preprimary_primary_level"
            ],
            [
              "Primary",
              "num_primary_level"
            ],
            [
              "Primary and junior secondary",
              "num_primary_js_level"
            ],
            [
              "Junior secondary",
              "num_js_level"
            ],
            [
              "Junior and senior secondary",
              "num_js_ss_level"
            ],
            [
              "Senior secondary",
              "num_ss_level"
            ],
            [
              "Primary, junior and senior secondary",
              "num_primary_js_ss_level"
            ],
            [
              "Other schools",
              "num_other_level"
            ],
            [
              "Pupil to teacher ratio",
              "student_teacher_ratio_lga"
            ],
            [
              "Percentage of teachers with NCE qualification",
              "proportion_teachers_nce"
            ],
            [
              "Classrooms in need of major repairs",
              "number_classrooms_need_major_repair"
            ]
          ],
          "health": [
            [
              "Health posts and dispensaries",
              "num_level_1_health_facilities"
            ],
            [
              "Primary health clinics",
              "num_level_2_health_facilities"
            ],
            [
              "Primary health centres",
              "num_level_3_health_facilities"
            ],
            [
              "Comprehensive health centres & hospitals",
              "num_level_4_health_facilities"
            ],
            [
              "Other health facillities",
              "num_level_other_health_facilities"
            ],
            [
              "Facilities that perform Caesarean sections",
              "num_health_facilities_c_sections"
            ],
            [
              "Skilled health providers per 1,000 population ",
              "num_skilled_health_providers_per_1000"
            ],
            [
              "CHEWs per 1,000 population",
              "num_chews_per_1000"
            ]
          ]
        }
    
def tmp_facility_indicators(lga, lga_data, lookup_data=True):
    def lga_data_lookup(slug):
        value_dict = lga_data.get(slug, None)
        if value_dict:
            return value_dict.get('value', None)
        else:
            return None

    def repeat_back(slug): return slug

    if lookup_data:
        g = lga_data_lookup
    else:
        g = repeat_back

    ilist = []
    islugs = {}
    sdata = _sector_slugs()
#    hi2s = [[x[0], g(x[1])] for x in islugs['health']]
    health_indicators = [
            ["Health posts and dispensaries", g("num_level_1_health_facilities")],
            ["Primary health clinics", g("num_level_2_health_facilities")],
            ["Primary health centres", g("num_level_3_health_facilities")],
            ["Comprehensive health centres & hospitals", g("num_level_4_health_facilities")],
            ["Other health facillities", g("num_level_other_health_facilities")],
            ["Facilities that perform Caesarean sections", g("num_health_facilities_c_sections")],
            ["Skilled health providers per 1,000 population ", g("num_skilled_health_providers_per_1000")],
            ["CHEWs per 1,000 population", g("num_chews_per_1000")],
        ]
    ilist.append(("health", "Health Facilities", health_indicators, g("num_health_facilities")))

    education_indicators = [
            ["Preprimary", g("num_preprimary_level")],
            ["Preprimary and primary", g("num_preprimary_primary_level")],
            ["Primary", g("num_primary_level")],
            ["Primary and junior secondary", g("num_primary_js_level")],
            ["Junior secondary", g("num_js_level")],
            ["Junior and senior secondary", g("num_js_ss_level")],
            ["Senior secondary", g("num_ss_level")],
            ["Primary, junior and senior secondary", g("num_primary_js_ss_level")],
            ["Other schools", g("num_other_level")],
            ["Pupil to teacher ratio", g("student_teacher_ratio_lga")],
            ["Percentage of teachers with NCE qualification", g("proportion_teachers_nce")],
            ["Classrooms in need of major repairs", g("number_classrooms_need_major_repair")],
        ]
    ilist.append(("education", "Schools", education_indicators, g("num_schools")))

    water_indicators = [
            ["Improved water points", g("num_improved_water_points")],
            ["- Overhead tanks", g("num_overhead_tanks")],
            ["- Taps", g("num_taps")],
            ["- Hand pumps", g("num_handpumps")],
            ["Percentage of improved water points that are functional", g("percentage_functional_improved")],
        ]
    ilist.append(("water", "Water Points", water_indicators, g("num_water_points")))
    return ilist
