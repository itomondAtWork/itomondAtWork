const {write_file_function, read_file_function} = require("./helper");

const request = process.argv[2];

if (request==="read") {
    read_file_function();
} else if (request==="write") {
    write_file_function();
} else {
    console.error("Forbidden");
}