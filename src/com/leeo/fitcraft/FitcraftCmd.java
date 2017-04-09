package com.leeo.fitcraft;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.ConnectException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLConnection;
import java.util.ArrayList;

import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.Material;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;
import org.bukkit.inventory.Inventory;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;

public class FitcraftCmd implements CommandExecutor{
    private final FitcraftMain plugin;
    
    private int fitcoin = 0;
    
    public FitcraftCmd(FitcraftMain instance){
        plugin = instance;
    }

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        // TODO Auto-generated method stub
        
        if(!(sender instanceof Player)){
            System.out.println("Impossible to user in bukkit");
            return false;
        }
        Player player = (Player) sender;
        
        if(args.length == 0){
            sender.sendMessage(">> FitCraft Help");
            sender.sendMessage(">> /fitcraft reward <fityou_id> <fityou_password> <amount>");
        }
        
        // start to get reward event
        {
            URLConnection urlConnectrion = null;
            
            // URL �ּ�
            if(args.length != 4){
                sender.sendMessage(">> /fitcraft reward <fityou_id> <fityou_password> <amount>");
            }
            else{
                try{
                    player.sendMessage("Start to get Fitcoin! 1 point = 1 Fitcoin");
                    
                    Runtime rt = Runtime.getRuntime();
                    String S_url = "http://fityou.xyz/fitapp/fitpoint/";
                    String user_id = args[1];
                    String password = args[2];
                    String point = args[3];
                    
                    fitcoin = Integer.parseInt(point);
                    // send URL
                    URL url = new URL(S_url+user_id+"/"+password+"/"+point);
                    System.out.println("url�� �������Դϴ�. url : " + S_url+user_id+"/"+password+"/"+point);
                    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                    URLConnection urlConnection = url.openConnection();
                    
                    //printByInputStream(urlConnection.getInputStream());
                    
                    BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream(),"UTF-8"));
                    //System.out.println(in);
                    String inputLine;
                    StringBuffer response = new StringBuffer();
                    
                    while ((inputLine = in.readLine()) != null) {
                        response.append(inputLine);
                    }
                    in.close();
                    
                    System.out.println("response : "+response);
                    if (response.toString().equals("200")){
                        ArrayList<String> newiteml = new ArrayList<>();
                        newiteml.add("");
                        newiteml.add(ChatColor.YELLOW + "Fitcoin");
                        
                        ItemStack newitem = new ItemStack(Material.NETHER_STAR);
                        ItemMeta newitemm = newitem.getItemMeta();
                        newitemm.setDisplayName("Fitcoin");
                        newitemm.setLore(newiteml);
                        newitem.setItemMeta(newitemm);
                        
                        Inventory inv = Bukkit.createInventory(null, 9 , ChatColor.LIGHT_PURPLE + "new inventory");
                        //inv.setItem(1, newitem);
                        //inv.addItem(newitem);
                        for (int reward = 0; reward < fitcoin; reward++)
                        {
                            player.getInventory().addItem(newitem);
                            inv.addItem(newitem);
                        }

                        
                        System.out.println(player.getName()+" success to get fitcoin");
                    }
                    else{
                        sender.sendMessage(">> /fitcraft reward fityou_id fityou_password fitcoin : to get a reward");
                    }

                } catch (ConnectException ce) {
                    System.out.println("fail to Connection");
                    ce.printStackTrace();
                } catch (IOException ie) {
                    System.out.println("fail to Connection2");
                    ie.printStackTrace();
                } catch (Exception e) {
                    System.out.println("fail to Connection3");
                    e.printStackTrace();
                } // try - catch
            }

                        
        }
        
        return false;
    }
}
