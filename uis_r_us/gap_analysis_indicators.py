def all_gap_indicators():
	return {
	    'health': [
	        {
	            'type': 'title',
	            'name': 'General'
	        },
	        {
	            'type': 'other',
	            'name': 'Population of the LGA',
	            'current': "pop_population",
	        },
	        {
	            'type': 'other',
	            'name': 'Population of the LGA (< 5 years)',
	            'current': "pop_u5",
	        },
	        {
	            'type': 'other',
	            'name': 'Number of Wards (estimated)',
	            'current': "num_wards_g",
	        },
	        {
	            'type': 'title',
	            'name': 'Facilities per Population'
	        },
	        {
	            'type': 'other',
	            'name': 'BHCs (including Health Posts and Dispensaries)',
	            'current': 'is_basic_care_g',
	            'target': 'bhc_per_pop_target_g'
	        },
	        {
	            'type': 'other',
	            'name': 'PHCs',
	            'current': 'is_primary_care_g',
	            'target': 'phc_per_pop_target_g'
	        },
	        {
	            'type': 'other',
	            'name': 'Health facilities with maternal health/emergency delivery capacity',
	            'current': 'facilities_delivery_capacity_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (BHCs needing construction)',
                'gap': 'bhc_gap_g'
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (PHCs needing construction)',
                'gap': 'phc_gap_g'
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (total health facilities needing repair)',
                'gap': 'facilities_need_repair_gap_g'
	        },
	        {
	            'type': 'title',
	            'name': 'Equipment/Infrastructure'
	        },
	        {
	            'type': 'other',
	            'name': 'Emergency referral transportation',
	            'current': 'emergency_transport_existing_g',
	            'target': 'emergency_transport_target_g'
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (emergency referral transportation to be purchased)',
	            'gap': 'emergency_transport_gap_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Healthcare facilities with water',
	            'current': 'water_access_g',
	            'target': 'facilities_water_target_g'
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (existing healthcare facilities needing water)',
	            'gap': 'existing_facilities_water_gap_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (new healthcare facilities needing water)',
	            'gap': 'new_facilities_water_gap_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Healthcare facilities with power',
	            'current': 'power_access_g',
	            'target': 'power_access_target_g'
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (existing healthcare facilities needing power)',
	            'gap': 'existing_facilities_power_gap_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (new healthcare facilities needing power)',
	            'gap': 'new_facilities_power_gap_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Healthcare facilities with sanitation',
	            'current': 'improved_sanitation_g',
	            'target': 'facilities_sanitation_target_g'
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (existing healthcare facilities needing sanitation)',
	            'gap': 'existing_facilities_sanit_gap_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (new healthcare facilities needing sanitation)',
	            'gap': 'new_facilities_sanit_gap_g',
	        },
	        {
	            'type': 'title',
	            'name': 'Drugs, Vaccines, and Diagnostics'
	        },
	        {
	            'type': 'other',
	            'name': 'Health facilities with essential medicines',
	            'current': 'essential_meds_existing_g',
	            'target': 'facilities_medicine_target_g'
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (existing healthcare facilities needing medicines)',
	            'gap': 'existing_facilities_med_gap_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (new healthcare facilities needing medicines)',
	            'gap': 'new_facilities_med_gap_g',
	        },
	        {
	            'type': 'title',
	            'name': 'Malaria Prevention/Treatment'
	        },
	        {
	            'type': 'other',
	            'name': 'Number of individuals sleeping under insecticide-treated bed nets',
	            'current': 'num_sleeping_under_net_existing_g',
	            'target': 'num_sleeping_under_net_target_g'
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (treated nets required for population)',
	            'gap': 'num_sleeping_under_net_gap_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Number of facilities equiped with Malaria treatment',
	            'current': 'malaria_tx_existing_g',
	            'target': 'malaria_tx_target_g'
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (existing healthcare facilities requiring malaria treatment)',
	            'gap': 'new_fac_malaria_tx_gap_g',
	        },
	        {
	            'type': 'title',
	            'name': 'Vaccines'
	        },
	        {
	            'type': 'other',
	            'name': 'Number of children <5 years routinely immunized',
	            'current': 'u5_immunized_existing_g',
	            'target': 'u5_immunized_target_g'
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (number of children needing to be immunized)',
	            'gap': 'u5_immunized_gap_g',
	        },
	        {
	            'type': 'title',
	            'name': 'Recurring Costs'
	        },
	        {
	            'type': 'other',
	            'name': 'Doctors',
	            'current': 'num_doctors_existing_g',
	            'target': 'num_doctors_target_g'
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (doctors needed)',
	            'gap': 'num_doctors_gap_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Nurses',
	            'current': 'num_nurses_existing_g',
	            'target': 'num_nurses_target_g'
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (nurses needed)',
	            'gap': 'num_nurses_gap_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Nurses/midwives',
	            'current': 'num_nursemidwives_existing_g',
	            'target': 'num_nursemidwives_target_g'
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (nurses/midwives needed)',
	            'gap': 'num_nursemidwives_gap_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Community health workers',
	            'current': 'num_chews_existing_g',
	            'target': 'num_chews_target_g'
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (community health workers needed)',
	            'gap': 'num_chews_gap_g',
	        },
	    ],
	    'education': [
            {
                'type': 'title',
                'name': 'General'
            },
            {
                'type': 'other',
                'name': 'Population of the LGA',
                'current': 'pop_population',
            },
            {
                'type': 'other',
                'name': 'Primary School age population (6 to 11 years)',
                'current': 'pop_school_going_age_6_11_g',
            },
            {
                'type': 'other',
                'name': 'Junior Secondary School age population (12 to 14 years)',
                'current': 'pop_school_going_age_12_14_g',
            },
	        {
	            'type': 'other',
	            'name': 'Students enrolled in primary education',
	            'current': 'gross_pry_enrollment_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Students enrolled in junior secondary education',
	            'current': 'gross_js_enrollment_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Students of primary school age (6 to 11 years ) enrolled in primary schools ',
	            'current': 'net_enrollment_pry1_pry6_total_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Students of primary school age (12 to 14 years ) enrolled in junior secondary schools ',
	            'current': 'net_enrollment_js1_js3_total_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (students of age not enrolled in primary school)',
	            'gap': 'gap_pry_enrollment_g',
	        },
            {
	            'type': 'title',
	            'name': 'Infrastructure'
	        },
	        {
	            'type': 'other',
	            'name': 'Schools with access to potable water',
	            'current': 'existing_water_g',
	            'target': 'target_supply_water_g'
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (water sources to be constructed at existing schools)',
	            'gap': 'gap_water_construct_existing_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (water sources to be constructed at new schools)',
	            'gap': 'gap_water_construct_new_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (water sources to be repaired)',
	            'gap': 'water_need_repair_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Schools with improved sanitation/toilet',
	            'current': 'existing_sanitation_g',
	            'target': 'target_sanitation_g'
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (sanitation infrastructure to be constructed at existing schools)',
	            'gap': 'gap_sani_existing_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (sanitation infrastructure to be constructed at new schools)',
	            'gap': 'gap_sani_new_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (existing sanitation needing repair)',
	            'gap': 'existing_sani_need_repair_g',
	        },
            {
	            'type': 'title',
	            'name': 'Furniture'
	        },
	        {
	            'type': 'other',
	            'name': 'Benches and chairs',
	            'current': 'existing_benches_g',
	            'target': 'target_benches_g'
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (bench/chairs to be purchased for existing schools)',
	            'gap': 'gap_benches_purchase_existing_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (bench/chairs to be purchased for new schools)',
	            'gap': 'gap_benches_purchase_new_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Desks',
	            'current': 'existing_desks_g',
	            'target': 'target_desks_g'
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (desks to be purchased for existing schools)',
	            'gap': 'gap_desks_purchase_existing_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (desks to be purchased for new schools)',
	            'gap': 'gap_desks_purchase_new_g',
	        },
            {
	            'type': 'title',
	            'name': 'Teaching Materials and Textbooks'
	        },
	        {
	            'type': 'other',
	            'name': 'Core Textbooks',
	            'current': 'existing_textbooks_g',
	            'target': 'target_textbooks_g'
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (textbooks to be purchased for existing schools)',
	            'gap': 'gap_textbooks_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Exercise books',
	            'current': 'existing_exercisebooks_g',
	            'target': 'target_exercisebooks_g'
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (exercise books to be purchased for existing schools)',
	            'gap': 'existing_exercisebooks_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Teaching tool sets',
	            'current': 'target_teaching_tool_sets_g',
	            'target': 'target_teaching_tool_sets_g'
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (teaching tool sets to be purchased for existing schools)',
	            'gap': 'gap_teaching_tool_sets_existing_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (teaching tool sets to be purchased for new schools)',
	            'gap': 'gap_teaching_tool_sets_new_g',
	        },
            {
	            'type': 'title',
	            'name': 'Teaching Staff'
	        },
	        {
	            'type': 'other',
	            'name': 'Qualified teachers',
	            'current': 'existing_qualifi_teachers_g',
	            'target': 'target_qualifi_teachers_g'
	        },
	        {
	            'type': 'other',
	            'name': 'Unqualified teachers',
	            'current': 'existing_unqualifi_teachers_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (new qualified teachers to be hired)',
	            'gap': 'gap_new_tchr_need_hired_g',
	        },
	        {
	            'type': 'other',
	            'name': 'Gap (unqualified teachers to be trained)',
	            'gap': 'gap_existing_tchr_need_train_g',
	        },
	    ]
	}
