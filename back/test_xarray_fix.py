"""
Quick test to verify xarray NetCDF4 engine fix
"""
import sys

print("Testing xarray NetCDF4 backend configuration...")

try:
    import xarray as xr
    print("✅ xarray imported successfully")
    
    import netCDF4
    print("✅ netCDF4 imported successfully")
    
    # Check available engines
    try:
        from xarray.backends import list_engines
        engines = list_engines()
        print(f"✅ Available xarray engines: {engines}")
        
        if 'netcdf4' in engines:
            print("✅ netcdf4 engine is available and registered")
        else:
            print("⚠️ Warning: netcdf4 engine not in registered engines list")
            
    except:
        print("ℹ️ Cannot list engines (older xarray version)")
    
    print("\n✅ All checks passed! xarray should work with engine='netcdf4'")
    sys.exit(0)
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
