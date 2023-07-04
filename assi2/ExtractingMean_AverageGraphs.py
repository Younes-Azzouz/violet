import pandas as pd
import matplotlib.pyplot as plt

# # # data0 = pd.read_csv('assi2/CSV Graphs/Seed0_pop_2min.csv')

# # # male_foxes = data0[data0['Agent Type'] == 'Foxfemale']
# # # female_foxes = data0[data0['Agent Type'] == 'Foxmale']
# # # male_rabbits = data0[data0['Agent Type'] == 'Rabbitmale']
# # # female_rabbits = data0[data0['Agent Type'] == 'Rabbitfemale']

# # # plt.plot(male_foxes['frame'], male_foxes['Population Count'], label='Male Foxes')
# # # plt.plot(female_foxes['frame'], female_foxes['Population Count'], label='Female Foxes')
# # # plt.plot(male_rabbits['frame'], male_rabbits['Population Count'], label='Male Rabbits')
# # # plt.plot(female_rabbits['frame'], female_rabbits['Population Count'], label='Female Rabbits')

# # # data1 = pd.read_csv('assi2/CSV Graphs/Seed1_pop_2min.csv')

# # # male_foxes1 = data1[data1['Agent Type'] == 'Foxfemale']
# # # female_foxes1 = data1[data1['Agent Type'] == 'Foxmale']
# # # male_rabbits1 = data1[data1['Agent Type'] == 'Rabbitmale']
# # # female_rabbits1 = data1[data1['Agent Type'] == 'Rabbitfemale']

# # # plt.plot(male_foxes1['frame'], male_foxes1['Population Count'], label='Male Foxes')
# # # plt.plot(female_foxes1['frame'], female_foxes1['Population Count'], label='Female Foxes')
# # # plt.plot(male_rabbits1['frame'], male_rabbits1['Population Count'], label='Male Rabbits')
# # # plt.plot(female_rabbits1['frame'], female_rabbits1['Population Count'], label='Female Rabbits')

# Plotting Everything in one:
file_paths = ['assi2\CSV Graphs\Seed0_pop_2min.csv', 'assi2\CSV Graphs\Seed1_pop_2min.csv', 'assi2\CSV Graphs\Seed2_pop_2min.csv', 'assi2\CSV Graphs\Seed3_pop_2min.csv', 'assi2\CSV Graphs\Seed4_pop_2min.csv', 'assi2\CSV Graphs\Seed5_pop_2min.csv', 'assi2\CSV Graphs\Seed6_pop_2min.csv', 'assi2\CSV Graphs\Seed7_pop_2min.csv', 'assi2\CSV Graphs\Seed8_pop_2min.csv',
'assi2\CSV Graphs\Seed9_pop_2min.csv', 'assi2\CSV Graphs\Seed10_pop_2min.csv', 'assi2\CSV Graphs\Seed11_pop_2min.csv', 'assi2\CSV Graphs\Seed12_pop_2min.csv', 'assi2\CSV Graphs\Seed13_pop_2min.csv', 'assi2\CSV Graphs\Seed14_pop_2min.csv', 'assi2\CSV Graphs\Seed15_pop_2min.csv', 'assi2\CSV Graphs\Seed16_pop_2min.csv', 'assi2\CSV Graphs\Seed17_pop_2min.csv', 'assi2\CSV Graphs\Seed18_pop_2min.csv',
'assi2\CSV Graphs\Seed19_pop_2min.csv']

data_frames = []
for file_path in file_paths:
    data_frames.append(pd.read_csv(file_path))

combined_data = pd.concat(data_frames)

# grouped_data = combined_data.groupby(['frame','Agent Type'])['Population Count'].agg(['mean', 'std']).reset_index()

# agent_types = grouped_data['Agent Type'].unique()

# for agent_type in agent_types:
#     agent_data = grouped_data[grouped_data['Agent Type'] == agent_type]
#     plt.errorbar(agent_data['frame'], agent_data['mean'], yerr=agent_data['std'], label=agent_type)
##################################
# Plotting each agent type on its own:
# agent_type_to_plot = 'Foxfemale' # <<< SPECIFY WHICH AGENT TO PLOT

# filtered_data = combined_data[combined_data['Agent Type'] == agent_type_to_plot]

# grouped_data = filtered_data.groupby('frame')['Population Count'].agg(['mean', 'std']).reset_index()

# # Plot the mean line with error bars representing the standard deviation
# plt.errorbar(grouped_data['frame'], grouped_data['mean'], yerr=grouped_data['std'], label=agent_type_to_plot)




# Specify the agent type you want to plot
agent_type_to_plot = 'Foxfemale'

# Filter the data for the specified agent type
filtered_data = combined_data[combined_data['Agent Type'] == agent_type_to_plot]

# Group the filtered data by 'Frames' and calculate the mean and standard deviation
grouped_data = filtered_data.groupby('frame')['Population Count'].agg(['mean', 'std']).reset_index()

# Calculate the mean for the specified agent type at each frame
mean_values = grouped_data['mean'].values

# Scale the mean values to make the line more visible
mean_scaled = mean_values * 1.5  # Adjust the scaling factor as needed

# Plot the individual agent type line
plt.errorbar(grouped_data['frame'], grouped_data['mean'], yerr=grouped_data['std'], label=agent_type_to_plot)

# Plot the mean line for the specified agent type as a fluctuating line
plt.plot(grouped_data['frame'], mean_values, color='red', linewidth= 4, label='Mean of Agent Type')

plt.xlabel('Frames')
plt.ylabel('Population count')

plt.legend()
plt.show()