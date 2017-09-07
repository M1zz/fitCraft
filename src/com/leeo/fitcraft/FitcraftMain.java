package com.leeo.fitcraft;

import org.bukkit.plugin.PluginManager;
import org.bukkit.plugin.java.JavaPlugin;

public class FitcraftMain extends JavaPlugin{
    //private static fitlogListener listener;
    private static FitcraftCmd command;
    
    public void onEnable(){
        initCommand();
        System.out.println("[FitCraft] Fitcraft v.1.0.9 Plugin is Enable.");
    }
    
    public void onDisable(){
        System.out.println("[FitCraft] FitCraft v.1.0.9 Plugin is Disable.");
    }
    
    public void initCommand(){
        command = new FitcraftCmd(this);
        getCommand("fitcraft").setExecutor(command);
    }
}