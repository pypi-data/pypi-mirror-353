# Kipu API Python library

[![PyPI version](https://badge.fury.io/py/kipu-python.svg)](https://badge.fury.io/py/kipu-python)
[![Python Support](https://img.shields.io/pypi/pyversions/kipu-python.svg)](https://pypi.org/project/kipu-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The Kipu Python library provides convenient access to the Kipu API from any Python 3.8+
application. The library includes HMAC SHA1 authentication, recursive JSON flattening capabilities and type definitions for most of the request params and response fields,
and offers asynchronous clients powered by [asyncio].

It is generated from our [KipuAPI V3 specification](https://api.kipuapi.com/api-docs/index.html)

## 🚀 Features

- ✅ **Complete API Coverage**: All 80+ Kipu API V3 endpoints implemented
- 🔐 **Secure Authentication**: HMAC SHA1 signature generation
- 📊 **Automatic Flattening**: Converts nested JSON responses to pandas DataFrames
- ⚡ **Async Support**: Built with asyncio for high performance
- 🛡️ **Error Handling**: Comprehensive exception hierarchy
- 📝 **Type Hints**: Full typing support for better development experience
- 🔄 **Flexible Response Format**: Choose between raw JSON or flattened DataFrames

## 📦 Installation

```bash
pip install kipu-python
```

## 🔧 Quick Start

```python
import asyncio
from kipu import KipuClient

async def main():
    async with KipuClient(
        access_id="your_access_id",
        secret_key="your_secret_key", 
        app_id="your_app_id"
    ) as client:
        
        # Get patient census as flattened DataFrame
        census_df = await client.get_patients_census()
        print(f"Found {len(census_df)} patients")
        
        # Get specific patient as raw JSON
        patient_data = await client.get_patient("patient_id", flatten=False)
        print(f"Patient: {patient_data['first_name']} {patient_data['last_name']}")

asyncio.run(main())
```

## 🔑 Authentication

The library handles HMAC SHA1 signature generation automatically. You need three credentials from Kipu:

- `access_id`: Your API access identifier
- `secret_key`: Your secret key for signature generation
- `app_id`: Your application ID (also called recipient_id)

## 📚 API Coverage

### Patient Management
```python
# Get patient census
census_df = await client.get_patients_census(params={
    "phi_level": "high",
    "page": 1,
    "per": 50
})

# Get specific patient
patient = await client.get_patient("patient_id")

# Create new patient
patient_data = {
    "document": {
        "recipient_id": app_id,
        "data": {
            "first_name": "John",
            "last_name": "Doe",
            "dob": "1990-01-01"
        }
    }
}
new_patient = await client.create_patient(patient_data)
```

### Medical Records
```python
# Get vital signs
vital_signs_df = await client.get_vital_signs()
patient_vitals = await client.get_patient_vital_signs("patient_id")

# Get allergies
allergies_df = await client.get_allergies()
patient_allergies = await client.get_patient_allergies("patient_id")

# Create vital signs
vital_data = {
    "document": {
        "recipient_id": app_id,
        "data": {
            "systolic_blood_pressure": 120,
            "diastolic_blood_pressure": 80,
            "heart_rate": 72
        }
    }
}
await client.create_patient_vital_signs("patient_id", vital_data)
```

### Appointments
```python
# Get appointments
appointments_df = await client.get_scheduler_appointments(params={
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
})

# Get patient appointments
patient_appointments = await client.get_patient_appointments("patient_id")
```

### Administrative
```python
# Get locations, users, providers
locations_df = await client.get_locations()
users_df = await client.get_users()
providers_df = await client.get_providers()
```

## 🔄 Response Processing

### Automatic Flattening (Default)
```python
# Returns a flattened pandas DataFrame
census_df = await client.get_patients_census()
print(type(census_df))  # <class 'pandas.core.frame.DataFrame'>
```

### Raw JSON Response
```python
# Returns raw JSON
census_data = await client.get_patients_census(flatten=False)
print(type(census_data))  # <class 'dict'> or <class 'list'>
```

### Global Flattening Control
```python
# Disable auto-flattening globally
async with KipuClient(
    access_id, secret_key, app_id,
    auto_flatten=False
) as client:
    raw_data = await client.get_patients_census()  # Raw JSON
    flat_data = await client.get_patients_census(flatten=True)  # DataFrame
```

## 🛡️ Error Handling

```python
from kipu.exceptions import (
    KipuAPIError,
    KipuAuthenticationError,
    KipuValidationError,
    KipuNotFoundError,
    KipuServerError
)

try:
    patient = await client.get_patient("invalid_id")
except KipuNotFoundError as e:
    print(f"Patient not found: {e.message}")
except KipuAuthenticationError as e:
    print(f"Authentication failed: {e.message}")
except KipuAPIError as e:
    print(f"API error: {e.message} (Status: {e.status_code})")
```

## 📎 File Uploads

```python
# Patient with attachment
patient_data = {
    "document[recipient_id]": app_id,
    "document[data][first_name]": "John",
    "document[data][last_name]": "Doe"
}

files = {
    "document[attachments_attributes][0][attachment]": {
        "content": file_bytes,
        "filename": "patient_id.jpg",
        "content_type": "image/jpeg"
    }
}

await client.create_patient(patient_data, files=files)
```

## 📋 Available Endpoints

### Core Categories
- **Patients**: Census, individual records, admissions, latest updates
- **Medical Records**: Vital signs, allergies, assessments, glucose logs
- **Evaluations**: Patient evaluations, evaluation templates
- **Appointments**: Scheduling, types, statuses, resources
- **Users & Providers**: User management, provider records, roles
- **Administrative**: Locations, care levels, flags, settings
- **Insurance**: Insurance records, verification
- **Groups**: Group sessions, patient groups

### Complete Method List
```python
# Patient endpoints
client.get_patients_census()
client.get_patient(patient_id)
client.create_patient(data)
client.update_patient(patient_id, data)
client.get_patients_admissions()
client.get_patients_latest()

# Medical records
client.get_vital_signs()
client.get_patient_vital_signs(patient_id)
client.create_patient_vital_signs(patient_id, data)
client.get_allergies()
client.get_patient_allergies(patient_id)
client.get_cows()
client.get_ciwa_ars()
client.get_glucose_logs()

# And 70+ more endpoints...
```

## 🧪 Development & Testing

```bash
# Clone the repository
git clone https://github.com/Rahulkumar010/kipu-python.git
cd kipu-python

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black kipu/
isort kipu/

# Type checking
mypy kipu/
```

## 📄 Requirements

- **Python**: 3.8+
- **Dependencies**:
  - `aiohttp>=3.8.0` - Async HTTP client
  - `pandas>=1.3.0` - Data manipulation
  - `numpy>=1.20.0` - Numerical computing
  - `tqdm>=4.60.0` - Progress bars

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📃 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Read the Docs](https://kipu-python.readthedocs.io/)
- **Issues**: [GitHub Issues](https://github.com/Rahulkumar010/kipu-python/issues)
- **Email**: rahul01110100@gmail.com

## 🏥 Healthcare Compliance

This library is designed for healthcare applications. Ensure your implementation complies with:
- HIPAA (Health Insurance Portability and Accountability Act)
- Local healthcare data protection regulations
- Kipu's terms of service and security requirements

---

**Built with ❤️ for the opensource community**
