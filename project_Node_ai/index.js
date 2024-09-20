const express = require('express');
const { exec } = require('child_process');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');
const knex = require('knex')({
    client: 'mysql',
    connection: {
        host: 'localhost',
        port: 8889,
        user: 'root',
        password: 'root',
        database: 'face_db'
    }
});

const app = express();
const port = 9999;

app.use(cors());
app.use(bodyParser.json());

app.use('/face_images', express.static('/Users/heroteam/Documents/python/node_api/face_images'));

app.get('/', (req, res) => {
    res.send('Hello World!');
});


app.get('/list-schedules', async (req, res) => {
    try {
        let rows = await knex('schedule').select();
        res.send({
            ok: 1,
            schedules: rows,
        });
    } catch (error) {
        res.send({
            ok: 0,
            error: error.message,
        });
    }
});

app.post('/set-time', async (req, res) => {
    const { start_time, end_time } = req.body;
    try {
        let ids = await knex('schedule').insert({ start_time, end_time });
        res.send({ ok: 1, id: ids });
    } catch (error) {
        res.send({ ok: 0, error: error.message });
    }
});


app.get('/liststds', async (req, res) => {
    let rows = await knex('passes');
    res.send({
        ok: 1,
        students: rows,
    });
});



app.get('/liststd', async (req, res) => {
    const { myParam } = req.query;
    console.log(myParam); // แสดงค่า id ที่ได้รับมาในคอนโซล

    try {
        if (!myParam) {
            return res.status(400).send({ ok: 0, message: 'ID is required' });
        }

        // ดึงข้อมูลจากฐานข้อมูลตาม time_id
        let rows = await knex('passes').where({ time_id: myParam }); // ใช้ชื่อคอลัมน์ที่ถูกต้อง

        if (rows.length === 0) {
            return res.status(404).send({ ok: 0, message: 'No records found for the provided ID' });
        }

        // ส่งข้อมูลที่ดึงมาให้ผู้ใช้
        res.send({
            ok: 1,
            data: rows,
            message: 'Data retrieved successfully',
        });
    } catch (error) {
        res.send({
            ok: 0,
            error: error.message,
        });
    }
});


app.post('/insert', async (req, res) => {
    console.log(req.body);
    let { username, password, email, file_path, count } = req.body;
    try {
        let ids = await knex('users')
            .insert({ username, password, email, file_path, count });
        res.send({ ok: 1, id: ids });
    } catch (error) {
        res.send({ ok: 0, error: error.message });
    }
});

app.post('/open_register', (req, res) => {
    exec('python3 vuejs_api/app/public/yovle8/register.py', (err, stdout, stderr) => {
        if (err) {
            console.error(`Error: ${stderr}`);
            res.status(500).send('Error opening file');
            return;
        }
        res.send('File opened successfully');
    });
});


app.post('/open_Examine', (req, res) => {
    const id = req.body.id; // Receive the ID from the request body

    if (typeof id !== 'string') {
        res.status(400).send('Invalid ID provided');
        return;
    }

    // Sanitize the input to avoid command injection
    const sanitizedId = id.replace(/[^a-zA-Z0-9]/g, '');

    // Execute the Python script and pass the ID as an argument
    exec(`python3 vuejs_api/app/public/yovle8/line2.py "${sanitizedId}"`, (err, stdout, stderr) => {
        if (err) {
            console.error(`Error: ${stderr}`);
            res.status(500).send('Error opening file');
            return;
        }
        res.send('File opened successfully');
    });
});


app.get('/schedule/:id', async (req, res) => {
    try {
        const id = req.params.id;
        const schedule = await knex('schedule').where('id', id).first();

        if (!schedule) {
            return res.status(404).json({ success: false, message: 'Schedule not found' });
        }

        res.json({ success: true, schedule });
    } catch (error) {
        console.error('Error fetching schedule:', error);
        res.status(500).json({ success: false, message: 'Internal Server Error' });
    }
});

// Route to delete a schedule and related passes
// Route to delete a schedule and related passes
// Route to delete a schedule and related passes using POST
app.post('/delete-schedule', async (req, res) => {
    const { id } = req.body;

    if (!id) {
        return res.status(400).json({ success: false, message: "ID is missing" });
    }

    try {
        // Delete related passes
        await knex('passes').where({ time_id: id }).del();

        // Delete the schedule
        const result = await knex('schedule').where({ id }).del();

        if (result) {
            res.json({ success: true, message: 'Schedule deleted successfully' });
        } else {
            res.json({ success: false, message: 'Schedule not found' });
        }
    } catch (error) {
        console.error('Error deleting schedule:', error); // Log the full error
        res.status(500).json({ success: false, message: 'Error deleting schedule', error: error.message });
    }
});

// Route to delete related passes directly using POST
app.post('/delete-passes', async (req, res) => {
    const { time_id } = req.body;

    if (!time_id) {
        return res.status(400).json({ success: false, message: "time_id is missing" });
    }

    try {
        // Delete the passes
        const result = await knex('passes').where({ time_id }).del();

        if (result) {
            res.json({ success: true, message: 'Passes deleted successfully' });
        } else {
            res.json({ success: false, message: 'No passes found for this time_id' });
        }
    } catch (error) {
        console.error('Error deleting passes:', error);
        res.status(500).json({ success: false, message: 'Error deleting passes' });
    }
});


// Endpoint to get staff list
app.get('/liststaffs', async (req, res) => {
    let rows = await knex('staffs');
    res.send({
        ok: 1,
        students: rows,
    });
});

app.post('/image_save', async (req, res) => {
    console.log(req.body);
    let { device, data_type, zone, sample, count, file_name, time_stamp } = req.body;
    try {
        let ids = await knex('image_save')
            .insert({ device, data_type, zone, sample, count, file_name, time_stamp })
            .returning('id');
        res.send({ ok: 1, id: ids });
    } catch (error) {
        res.send({ ok: 0, error: error.message });
    }
});

app.post('/delete_face', (req, res) => {
    const { id } = req.body;

    if (!id) {
        return res.status(400).json({ success: false, message: "ID is missing" });
    }

    // Update the code to use knex for deletion
    knex('staffs').where({ id }).del()
        .then((result) => {
            if (result === 0) {
                return res.status(404).json({ success: false, message: "Record not found" });
            }
            res.json({ success: true, message: "Record deleted successfully" });
        })
        .catch((error) => {
            console.error("Error deleting the record:", error);
            res.status(500).json({ success: false, message: "Error deleting the record" });
        });
});

app.post('/delete', (req, res) => {
    const { id } = req.body;

    if (!id) {
        return res.status(400).json({ success: false, message: "ID is missing" });
    }

    // Update the code to use knex for deletion
    knex('passes').where({ id }).del()
        .then((result) => {
            if (result === 0) {
                return res.status(404).json({ success: false, message: "Record not found" });
            }
            res.json({ success: true, message: "Record deleted successfully" });
        })
        .catch((error) => {
            console.error("Error deleting the record:", error);
            res.status(500).json({ success: false, message: "Error deleting the record" });
        });
});

app.post('/update', async (req, res) => {
    console.log(req.body);
    let { id, username, password, email } = req.body;
    try {
        let rows = await knex('users').where({ id })
            .update({ username, password, email });
        res.send({ ok: 1, id: rows });
    } catch (error) {
        res.send({ ok: 0, error: error.message });
    }
});


app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
});
