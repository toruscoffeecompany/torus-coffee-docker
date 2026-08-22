Add-Type @"
using System;
using System.Diagnostics;
using System.Management;

public class ProcessMonitor {
    public static void Main() {
        ManagementEventWatcher watcher = new ManagementEventWatcher();
        WqlEventQuery query = new WqlEventQuery("SELECT * FROM __InstanceCreationEvent WITHIN 0.1 TARGETINSTANCE OF Win32_Process WHERE TargetInstance.Name='cmd.exe'");
        
        watcher.EventArrived += (sender, e) => {
            var instance = (ManagementBaseObject)e.NewEvent["TargetInstance"];
            string pid = instance["ProcessId"].ToString();
            string ppid = instance["ParentProcessId"].ToString();
            
            Console.WriteLine($"CMD_SPAWN: PID={pid} ParentPID={ppid}");
            
            // Get parent process name
            try {
                var parent = new ManagementObject($"Win32_Process.Handle='{ppid}'");
                parent.Get();
                Console.WriteLine($"  Parent: {parent["Name"]} Cmd:{(parent["CommandLine"] ?? "").Substring(0, Math.Min(100, (parent["CommandLine"] ?? "").Length))}");
            } catch (Exception ex) {
                Console.WriteLine($"  Parent lookup error: {ex.Message}");
            }
            
            // Kill cmd.exe
            try { Process.GetProcessById(int.Parse(pid)).Kill(true); } catch {}
        };
        
        watcher.Start();
        Console.WriteLine("CMD_SPAWN_MONITOR: Active — watching for cmd.exe creation");
        Console.WriteLine("Monitoring for 35 seconds...");
        System.Threading.Thread.Sleep(35000);
        Console.WriteLine("DONE");
    }
}
"@

[ProcessMonitor]::Main()
