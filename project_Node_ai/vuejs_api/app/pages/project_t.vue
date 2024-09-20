<template>
    <v-container>
      <v-card class="elevation-2 pa-4">
        <v-card-title class="bg-primary text-white">
          <v-toolbar flat>
            <v-toolbar-title>กำหนดเวลาใหม่</v-toolbar-title>
          </v-toolbar>
        </v-card-title>
  
        <v-form @submit.prevent="setTime">
          <v-text-field
            v-model="start_time"
            label="เวลาเริ่มต้น"
            type="datetime-local"
            required
          ></v-text-field>
  
          <v-text-field
            v-model="end_time"
            label="เวลาสิ้นสุด"
            type="datetime-local"
            required
          ></v-text-field>
  
          <v-btn color="primary" type="submit">บันทึกเวลา</v-btn>
        </v-form>
      </v-card>
    </v-container>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data: () => ({
      start_time: '',
      end_time: '',
    }),
  
    methods: {
      async setTime() {
        try {
          await axios.post('http://localhost:9999/set-time', {
            start_time: this.start_time,
            end_time: this.end_time,
          });
          this.$router.push('/');
        } catch (error) {
          console.error('Error setting time:', error);
        }
      },
    },
  };
  </script>
  