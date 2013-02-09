def tmp_get_mdg_indicators(lga_data, g):
    return [
        ("Goal 1: Eradicate extreme poverty and hunger", [
            [None, "Percentage of children under five who are underweight (weight-for-age)", g("prevalence_of_underweight_children_u5")],
            [None, "Percentage of children under five with stunting (height-for-age)", g("prevalence_of_stunting_children_u5")],
            [None, "Percentage of children under five with wasting (weight-for-height)", g("prevalence_of_wasting_children_u5")],
        ]),
        ("Goal 2: Achieve universal primary education", [
            [None, "Net enrollment rate for primary education", g("net_enrollment_ratio_primary_education")],
            [None, "Gross enrollment rate in primary education", g("gross_enrollment_rate_primary")],
            [None, "Net enrollment rate for secondary education", g("net_enrollment_ratio_secondary_education")],
            [None, "Gross enrollment rate in secondary education", g("gross_enrollment_ratio_secondary_education")],
            [None, "Literacy rate of 15-24 year olds (men and women)", g("literacy_rate")],
        ]),
        ("Goal 3: Promote gender equality and empower women", [
            [None, "Ratio of girls to boys in primary schools", g("girl_boy_ratio_primary")],
            [None, "Ratio of girls to boys in junior secondary schools", g("girl_boy_ratio_js")],
            [None, "Ratio of girls to boys in senior secondary schools ", g("girl_boy_ratio_secondary_school")],
            [None, "Gender parity index (GPI) for primary schools", g("gender_parity_index_primary")],
            [None, "Gender parity index (GPI) for junior secondary schools", g("gender_parity_index_js")],
        ]),
        ("Goal 4: Reduce child mortality", [
            [None, "Under five mortality rate (per 1,000 live births)", g("mortality_rate_children_u5")],
            [None, "Infant mortality rate (per 1,000 live births)", g("mortality_rate_infant")],
            [None, "Measles immunization rate", g("immunization_rate_measles")],
            [None, "DPT 3 immunization rate", g("immunization_rate_dpt3")],
            [None, "Percentage of children under five years of age with diarrhea who received oral rehydration therapy", g("proportion_of_children_u5_diarrhea_treated_with_ors_med")],
        ]),
        ("Goal 5: Improve maternal health", [
            [None, "Maternal mortality", g("mortality_rate_maternal")],
            [None, "Percentage of births attended by a skilled birth attendant", g("proportion_of_births_by_skilled_health_personnel")],
            [None, "Percentage of women who attended at least four antenatal visits", g("percent_antenatal_care_four")],
            [None, "Percentage of pregnant women tested for HIV", g("percentage_pregnant_women_tested_for_hiv_during_pregnancy")],
        ]),
        ("Goal 6: Combat HIV/AIDS, malaria and other diseases", [
            [None, "HIV Prevalence", g("prevalence_of_hiv")],
            [None, "Percentage of men and women ever tested for HIV", g("percentage_of_individuals_tested_for_hiv_ever")],
            [None, "Percentage of children under five sleeping under insecticide-treated bednets", g("proportion_children_u5_sleeping_under_itns")],
            [None, "Tuberculosis treatment success rate", g("tb_treatment_success_rate")],
        ]),
        ("Goal 7: Ensure environmental sustainability", [
            [None, "Percentage of households with access to an improved water source", g("percentage_households_with_access_to_improved_water_sources")],
            [None, "Percentage of households with access to improved sanitation", g("percentage_households_with_access_to_improved_sanitation")],
        ]),
    ]