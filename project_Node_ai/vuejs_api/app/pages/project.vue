<template>
  <v-container>
    <v-card class="elevation-2 pa-4">
      <v-card-title class="bg-primary text-white">
        <v-toolbar flat>
          <v-toolbar-title>List</v-toolbar-title>
          <v-spacer></v-spacer>
          <!-- Conditionally render the Examine button -->
          <v-btn v-if="!isTimeExpired" color="primary" @click="openExamine">Examine</v-btn>
          <v-btn color="error" @click="goToProjectF">Exit</v-btn>
        </v-toolbar>
      </v-card-title>
      <v-data-table
        :headers="headers"
        :items="desserts"
        :sort-by="[{ key: 'timestamp', order: 'asc' }]"
        item-key="id"
        class="elevation-1 mt-4"
      >
        <template v-slot:item.actions="{ item }">
          <v-icon class="me-2" size="small" @click="confirmDelete(item)" color="red">
            mdi-delete
          </v-icon>
        </template>
        <template v-slot:item.timestamp="{ item }">
          {{ formatTimestamp(item.timestamp) }}
        </template>
        <template v-slot:item.image_path="{ item }">
          <v-btn @click="openDialog(item.image_path)" class="pa-0">
            <v-img :src="`/yovle8/${item.image_path}`" max-width="100" max-height="100" contain class="rounded-lg border border-grey lighten-2"></v-img>
          </v-btn>
        </template>
        <template v-slot:item.direction="{ item }">
          <div :style="{ color: item.direction === 'IN' ? 'green' : 'red', fontWeight: item.direction === 'IN' ? 'bold' : 'normal' }">
            {{ item.direction }}
            <v-icon small class="ml-2" :style="{ color: item.direction === 'IN' ? 'green' : 'red' }">
              mdi-circle
            </v-icon>
          </div>
        </template>
        <template v-slot:no-data>
          <v-btn color="primary" @click="initialize">
            Reset
          </v-btn>
        </template>
      </v-data-table>

      <!-- Image Viewing Dialog -->
      <v-dialog v-model="dialog" max-width="80%">
        <v-card>
          <v-card-title class="bg-primary text-white">
            <span class="headline">Image</span>
          </v-card-title>
          <v-card-text>
            <v-img :src="currentImage" contain class="rounded-lg"></v-img>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="secondary" @click="closeDialog">Close</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Schedule Info -->
      <v-card class="mt-4">
        <v-card-title class="bg-primary text-white">
          <span class="headline">Schedule Details</span>
        </v-card-title>
        <v-card-text>
          <div v-if="schedule">
            <p><strong>Start Time:</strong> {{ formatTimestamp(schedule.start_time) }}</p>
            <p><strong>End Time:</strong> {{ formatTimestamp(schedule.end_time) }}</p>
            <p v-if="isTimeExpired" class="error">Time has expired</p>
            <p v-else>Time is still valid</p>
          </div>
          <div v-else>
            <p>Loading schedule...</p>
          </div>
        </v-card-text>
      </v-card>
    </v-card>

    <!-- Confirmation Dialog -->
    <v-dialog v-model="dialogDelete" max-width="300px">
      <v-card>
        <v-card-title class="bg-primary text-white">
          <span class="headline">Confirm Delete</span>
        </v-card-title>
        <v-card-text>
          Are you sure you want to delete this item?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="deleteItemConfirm">Yes</v-btn>
          <v-btn color="secondary" @click="closeDelete">No</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import axios from 'axios';
import { format } from 'date-fns';

export default {
  data() {
    return {
      myParam: this.$route.query.myParam || 'default value',
      ids: '',
      dialogDelete: false,
      dialog: false,
      currentImage: '',
      headers: [
        { text: 'ID', value: 'id' },
        { text: 'Name', value: 'name' },
        { text: 'Direction', value: 'direction' },
        { text: 'Timestamp', value: 'timestamp' },
        { text: 'Image', value: 'image_path' },
        { text: 'Actions', value: 'actions', sortable: false }
      ],
      desserts: [],
      editedIndex: -1,
      editedItem: {},
      defaultItem: {},
      schedule: null,
      isTimeExpired: false,
    };
  },

  computed: {
    formTitle() {
      return this.editedIndex === -1 ? 'Add Data' : 'Edit Data';
    },
  },

  watch: {
    '$route.query.myParam': {
      immediate: true,
      handler(newVal) {
        this.myParam = newVal;
        this.fetchSchedule(); // Fetch schedule when `myParam` changes
      },
    },
    dialogDelete(val) {
      val || this.closeDelete();
    },
  },

  async created() {
    this.initialize();
  },

  methods: {
    async confirmDelete(item) {
      console.log("Confirming delete for ID:", item.id);
      this.ids = item.id;
      this.dialogDelete = true;
    },

    async deleteItemConfirm() {
      if (this.ids) {
        try {
          console.log("Attempting to delete ID:", this.ids);
          const response = await axios.post('http://localhost:9999/delete', { id: this.ids });

          console.log("Delete response:", response.data);
          
          if (response.data.success) {
            await this.loadDesserts();
          } else {
            console.error("Failed to delete the record:", response.data.message);
          }

          this.closeDelete();
        } catch (error) {
          console.error("Error during deletion:", error);
        }
      }
    },

    async openExamine() {
      try {
        const response = await axios.post('http://localhost:9999/open_Examine', { id: this.myParam });
        console.log('Examine file opened with ID:', this.myParam);
      } catch (error) {
        console.error('Error opening file:', error);
      }
    },

    async loadDesserts() {
      try {
        const params = { myParam: this.myParam };
        const response = await axios.get('http://localhost:9999/liststd', { params });
        this.desserts = response.data.data;
        console.log("Loaded desserts:", this.desserts);
      } catch (error) {
        console.error("Error loading desserts:", error);
      }
    },

    async fetchSchedule() {
      try {
        const response = await axios.get(`http://localhost:9999/schedule/${this.myParam}`);
        if (response.data.success) {
          this.schedule = response.data.schedule;
          this.checkTimeExpiry(this.schedule.end_time);
        } else {
          console.error("Failed to fetch schedule:", response.data.message);
        }
      } catch (error) {
        console.error("Error fetching schedule:", error);
      }
    },

    checkTimeExpiry(endTime) {
      const currentTime = new Date();
      const endTimeDate = new Date(endTime);
      this.isTimeExpired = currentTime > endTimeDate;
    },

    initialize() {
      this.loadDesserts();
    },

    closeDelete() {
      this.dialogDelete = false;
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem);
        this.editedIndex = -1;
      });
    },

    openDialog(imagePath) {
      // Prepend the correct directory path
      this.currentImage = `/yovle8/${imagePath}`;
      this.dialog = true;
    },

    closeDialog() {
      this.dialog = false;
    },

    formatTimestamp(timestamp) {
      return format(new Date(timestamp), 'yyyy-MM-dd HH:mm:ss');
    },

    goToProjectF() {
      this.$router.push({ path: '/project_f' });
    },
  },
};
</script>

<style scoped>
.error {
  color: red;
}
.bg-green {
  background-color: #e0f2f1;
}
.bg-yellow {
  background-color: #fffde7;
}
</style>
