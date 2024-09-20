<template>
  <v-container>
    <v-card class="elevation-2 pa-4">
      <v-card-title class="bg-primary text-white">
        <v-toolbar flat>
          <v-toolbar-title>รายชื่อสมาชิก</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn color="secondary" @click="openRegister">Register</v-btn>
          <v-btn color="error" @click="goToProjectF">Exit</v-btn>
        </v-toolbar>
      </v-card-title>
      
      <v-data-table
        :headers="headers"
        :items="staffs"
        item-key="id"
        class="elevation-1 mt-4"
        :items-per-page="5"
        item-class="my-2"
      >
        <template v-slot:item.face_img="{ item }">
          <img :src="`/yovle8/${item.face_img}`" alt="Face Image" width="50" />
        </template>
        <template v-slot:item="{ item }">
          <tr>
            <td>{{ item.displayName }}</td>
            <td>{{ item.dept }}</td>
            <td>
              <img :src="`/yovle8/${item.face_img}`" alt="Face Image" width="50" />
            </td>
            <td>
              <v-icon class="me-2" size="small" @click="deleteItem(item)" color="red">
                mdi-delete
              </v-icon>
            </td>
          </tr>
        </template>
        <template v-slot:no-data>
          <v-btn color="primary" @click="initialize">Reset</v-btn>
        </template>
      </v-data-table>

      <!-- Delete Confirmation Dialog -->
      <v-dialog v-model="dialogDelete" max-width="500px">
        <v-card>
          <v-card-title class="headline">Are you sure you want to delete this item?</v-card-title>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="green darken-1" @click="deleteItemConfirm">Yes</v-btn>
            <v-btn color="red darken-1" @click="closeDelete">No</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-card>
  </v-container>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      dialogDelete: false,
      currentItem: null,
      headers: [
        { text: 'Name', value: 'displayName' },
        { text: 'Department', value: 'dept' },
        { text: 'Face Image', value: 'face_img' },
        { text: 'Actions', value: 'actions', sortable: false }
      ],
      staffs: [],
    };
  },

  created() {
    this.initialize();
  },

  methods: {
    async fetchStaffs() {
      try {
        const response = await axios.get('http://localhost:9999/liststaffs');
        if (response.data.ok) {
          this.staffs = response.data.students;
          console.log('Fetched staff data:', this.staffs);
        } else {
          console.error('Error fetching staff data:', response.data);
        }
      } catch (error) {
        console.error('Error fetching staff data:', error);
      }
    },

    deleteItem(item) {
      this.currentItem = item;
      this.dialogDelete = true;
    },

    async deleteItemConfirm() {
      if (this.currentItem) {
        try {
          const response = await axios.post('http://localhost:9999/delete_face', { id: this.currentItem.id });
          if (response.data.success) {
            this.initialize();
          } else {
            console.error("Failed to delete the record:", response.data.message);
          }
        } catch (error) {
          console.error("Error during deletion:", error);
        }
      }
      this.closeDelete();
    },

    closeDelete() {
      this.dialogDelete = false;
      this.currentItem = null;
    },

    async openRegister() {
      try {
        await axios.post('http://localhost:9999/open_register');
        console.log('Register file opened');
      } catch (error) {
        console.error('Error opening file:', error);
      }
    },
    
    goToProjectF() {
      this.$router.push({ path: '/project_f' });
    },

    initialize() {
      this.fetchStaffs();
    }
  }
};
</script>

<style scoped>
.v-card {
  border-radius: 10px;
}

.v-card-title {
  border-bottom: 2px solid #fff;
}

.v-btn {
  border-radius: 20px;
}

.v-data-table th {
  background-color: #f5f5f5;
  font-weight: bold;
}

.v-data-table td img {
  border-radius: 5px;
}

.my-2 {
  margin: 8px 0;
}
</style>
