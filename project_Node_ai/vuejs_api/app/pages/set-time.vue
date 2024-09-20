<template>
    <v-container>
      <v-card class="elevation-2 pa-4">
        <v-card-title class="bg-primary text-white">
          <v-toolbar flat>
            <v-toolbar-title>กำหนดเวลาใหม่</v-toolbar-title>
          </v-toolbar>
        </v-card-title>
  
        <v-form ref="form" @submit.prevent="setTime">
          <v-text-field
            v-model="start_time"
            label="เวลาเริ่มต้น"
            type="datetime-local"
            required
            :rules="[rules.required]"
          ></v-text-field>
  
          <v-text-field
            v-model="end_time"
            label="เวลาสิ้นสุด"
            type="datetime-local"
            required
            :rules="[rules.required]"
          ></v-text-field>
  
          <v-btn color="primary" type="submit">บันทึกเวลา</v-btn>
        </v-form>
      </v-card>
  
      <!-- Snackbar for success message -->
      <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="3000">
        {{ snackbarMessage }}
        <v-btn text @click="snackbar = false">Close</v-btn>
      </v-snackbar>
    </v-container>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data: () => ({
      start_time: '',
      end_time: '',
      snackbar: false,
      snackbarColor: 'success',
      snackbarMessage: '',
      rules: {
        required: value => !!value || 'This field is required',
      },
    }),
  
    methods: {
      async setTime() {
        const form = this.$refs.form;
  
        // Validate the form
        if (!form.validate()) {
          this.snackbarColor = 'error';
          this.snackbarMessage = 'ข้อมูลไม่ครบ';
          this.snackbar = true;
          return;
        }
  
        try {
          await axios.post('http://localhost:9999/set-time', {
            start_time: this.start_time,
            end_time: this.end_time,
          });
          this.snackbarColor = 'success';
          this.snackbarMessage = 'บันทึกเรียบร้อยแล้ว';
          this.snackbar = true;
  
          setTimeout(() => {
            this.$router.push('project_f');
          }, 3000);
        } catch (error) {
          console.error('Error setting time:', error);
          this.snackbarColor = 'error';
          this.snackbarMessage = 'เกิดข้อผิดพลาดในการบันทึกเวลา';
          this.snackbar = true;
        }
      },
    },
  };
  </script>
  
  <style scoped>
  /* Optional: Add any additional styling here */
  </style>
  