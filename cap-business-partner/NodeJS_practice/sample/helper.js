const fs = require('node:fs');

const person = {
    name: "Mike",
    age: 34
}

const read_file_function = function() {
    fs.readFile("./sample.json", "utf8", function(err, data) {
        const person = JSON.parse(data)
        console.log(person.name);
        });
    };

const write_file_function = function() {
    fs.writeFile("sample.json", JSON.stringify(person), function() {
        console.log("Writing done!");
        });
    };

module.exports = {
    write_file_function: write_file_function,
    read_file_function: read_file_function
};


