# CAP Business Partner Application

This project is a SAP Cloud Application Programming (CAP) model for managing business partners. It includes a database schema, sample data, and a service definition for CRUD operations on business partner entities.

## Project Structure

- **db/schema.cds**: Defines the database schema, including the `BusinessPartner` entity with properties:
  - `BusinessPartner` (ID)
  - `FirstName`
  - `LastName`
  - `Email`

- **db/data/BusinessPartner.csv**: Contains sample data for business partners:
  1. `BP001, John, Doe, john.doe@example.com`
  2. `BP002, Jane, Smith, jane.smith@example.com`
  3. `BP003, Alice, Johnson, alice.johnson@example.com`
  4. `BP004, Bob, Brown, bob.brown@example.com`
  5. `BP005, Charlie, Davis, charlie.davis@example.com`

- **srv/service.cds**: Defines the service for CRUD operations on the `BusinessPartner` entity.

- **.cdsrc.json**: Contains configuration settings for the CAP project, including database connection settings.

- **package.json**: Lists the project's dependencies and scripts for npm.

- **.gitignore**: Specifies files and directories to be ignored by Git.

## Getting Started

To get started with this project, ensure you have the necessary dependencies installed. You can run the following command to install them:

```
npm install
```

After installing the dependencies, you can run the application using:

```
npm start
```

## Sample Data

The following sample business partner entries are included in the project:

1. **Business Partner ID**: BP001
   - First Name: John
   - Last Name: Doe
   - Email: john.doe@example.com

2. **Business Partner ID**: BP002
   - First Name: Jane
   - Last Name: Smith
   - Email: jane.smith@example.com

3. **Business Partner ID**: BP003
   - First Name: Alice
   - Last Name: Johnson
   - Email: alice.johnson@example.com

4. **Business Partner ID**: BP004
   - First Name: Bob
   - Last Name: Brown
   - Email: bob.brown@example.com

5. **Business Partner ID**: BP005
   - First Name: Charlie
   - Last Name: Davis
   - Email: charlie.davis@example.com

## License

This project is licensed under the MIT License.