<template>
  <v-container fluid>
    <v-card class="elevation-2 pa-4">
      <v-card-title class="bg-primary text-white">
        <v-toolbar flat>
          <v-toolbar-title class="headline">Schedule List</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn color="secondary" @click="openRegister_Face" class="mr-2">
            <v-icon left>mdi-account-plus</v-icon>
            Register Face
          </v-btn>
          <v-btn color="secondary" @click="goToSetTime">
            <v-icon left>mdi-clock-outline</v-icon>
            Set Time
          </v-btn>
        </v-toolbar>
      </v-card-title>

      <v-data-table
        :headers="headers"
        :items="schedules"
        item-key="id"
        class="elevation-1 mt-4"
      >
        <template v-slot:item="{ item }">
          <tr :class="getRowClass(item)">
            <td>{{ formatTimestamp(item.start_time) }}</td>
            <td>{{ formatTimestamp(item.end_time) }}</td>
            <td>
          
              <v-btn
                color="success"
                @click="goToProject(item.id)"
                class="ma-1"
                rounded
                small
              >
                <v-icon left>mdi-folder-open</v-icon>
                Go to Project
              </v-btn>
              <v-btn
                color="error"
                @click="confirmDeleteSchedule(item.id)"
                class="ma-1"
                rounded
                small
              >
                <v-icon left>mdi-delete</v-icon>
                Delete
              </v-btn>
              <div v-if="isBeforeStartTime(item)" class="status-text status-not-started">
                <v-icon>mdi-timer-sand</v-icon> Not Started Yet
              </div>
              <div v-else-if="isWithinTime(item)" class="status-text status-ongoing">
                <v-icon>mdi-timer</v-icon> Ongoing
              </div>
              <div v-else class="status-text status-time-over">
                <v-icon>mdi-timer-off</v-icon> Time Over
              </div>
            </td>
          </tr>
        </template>
      </v-data-table>
    </v-card>

    <!-- Confirmation Dialog -->
    <v-dialog v-model="showConfirmDialog" max-width="400px">
      <v-card>
        <v-card-title class="headline">Confirm Delete</v-card-title>
        <v-card-text>
          Are you sure you want to delete this schedule? This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="cancelDelete" class="mr-2">
            <v-icon left>mdi-cancel</v-icon>
            Cancel
          </v-btn>
          <v-btn color="error" @click="deleteScheduleConfirmed">
            <v-icon left>mdi-delete</v-icon>
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import axios from 'axios';
import { format } from 'date-fns';

export default {
  data: () => ({
    headers: [
      { text: 'Start Time', value: 'start_time' },
      { text: 'End Time', value: 'end_time' },
      { text: 'Actions', value: 'actions' },
    ],
    schedules: [],
    showConfirmDialog: false,
    scheduleToDelete: null,
  }),

  async created() {
    this.loadSchedules();
  },

  methods: {
    async loadSchedules() {
      try {
        const response = await axios.get('http://localhost:9999/list-schedules');
        this.schedules = response.data.schedules;
      } catch (error) {
        console.error('Error loading schedules:', error);
      }
    },

    formatTimestamp(timestamp) {
      return format(new Date(timestamp), 'dd MMMM yyyy HH:mm:ss');
    },

    isWithinTime(item) {
      const now = new Date();
      const startTime = new Date(item.start_time);
      const endTime = new Date(item.end_time);
      return now >= startTime && now <= endTime;
    },

    isBeforeStartTime(item) {
      const now = new Date();
      const startTime = new Date(item.start_time);
      return now < startTime;
    },

    getRowClass(item) {
      if (this.isWithinTime(item)) {
        return 'row-green';
      } else if (this.isBeforeStartTime(item)) {
        return 'row-blue';
      } else {
        return 'row-red';
      }
    },

    async openExamine(id) {
      try {
        await axios.post('http://localhost:9999/open_Examine', { id });
        console.log('Examine file opened');
      } catch (error) {
        console.error('Error opening file:', error);
      }
    },

    goToSetTime() {
      this.$router.push('/set-time');
    },
    
    openRegister_Face() {
      this.$router.push({ path: '/register' });
    },

    async goToProject(id) {
      try {
        this.$router.push({ path: '/project', query: { myParam: id } });
      } catch (error) {
        console.error('Error sending ID:', error);
      }
    },

    confirmDeleteSchedule(id) {
      this.scheduleToDelete = id;
      this.showConfirmDialog = true;
    },

    async deleteScheduleConfirmed() {
      try {
        const deleteScheduleResponse = await axios.post('http://localhost:9999/delete-schedule', { id: this.scheduleToDelete });
        if (deleteScheduleResponse.data.success) {
          console.log('Schedule deleted');
          this.loadSchedules();
        } else {
          console.error('Failed to delete schedule:', deleteScheduleResponse.data.message);
        }
      } catch (error) {
        console.error('Error deleting schedule:', error);
      }
      this.showConfirmDialog = false;
      this.scheduleToDelete = null;
    },

    cancelDelete() {
      this.showConfirmDialog = false;
      this.scheduleToDelete = null;
    },
  },
};
</script>

<style scoped>
.v-card {
  background: #fff;
  border-radius: 8px;
}

.v-toolbar-title {
  font-size: 1.25rem;
  font-weight: 600;
}

.v-data-table {
  border-radius: 8px;
  overflow: hidden;
}

.v-data-table th,
.v-data-table td {
  padding: 16px;
}

.row-green {
  background-color: #e8f5e9; /* Light green */
}

.row-red {
  background-color: #fce4ec; /* Light red */
}

.row-blue {
  background-color: #e3f2fd; /* Light blue */
}

.status-text {
  margin-top: 4px;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-not-started {
  color: #0288d1; /* Blue */
}

.status-ongoing {
  color: #388e3c; /* Green */
}

.status-time-over {
  color: #d32f2f; /* Red */
}

.v-dialog .v-card {
  border-radius: 8px;
}

.v-btn {
  border-radius: 20px; /* Rounded buttons */
}

.v-card-actions .v-btn {
  border-radius: 20px; /* Rounded corners for buttons */
}

.v-icon {
  margin-right: 8px; /* Spacing between icon and text */
}
</style>
