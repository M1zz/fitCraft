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
import org.bukkit.inventory.meta.PotionMeta;
import org.bukkit.potion.Potion;
import org.bukkit.potion.PotionEffect;
import org.bukkit.potion.PotionEffectType;
import org.bukkit.potion.PotionType;

public class FitcraftCmd implements CommandExecutor{
    private final FitcraftMain plugin;
    
    private int fitcoin = 0;
    private int fitSleep = 0;
    private int fitHeart = 0;
    
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
        if(args[0].equals("reward"))
        {
            URLConnection urlConnectrion = null;
            
            // URL 주소
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
                    System.out.println("url에 연결중입니다. url : " + S_url+user_id+"/"+password+"/"+point);
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
        else if (args[0].equals("sleep")){
            URLConnection urlConnectrion = null;
            
            // URL 주소
            if(args.length != 4){
                sender.sendMessage(">> /fitcraft sleep <fityou_id> <fityou_password> <Amount>");
            }
            else{
                try{
                    player.sendMessage("Start to get Sleep reward! 1 hour = 1 EXP bottle");
                    
                    Runtime rt = Runtime.getRuntime();
                    String S_url = "http://fityou.xyz/fitapp/fitSleep/";
                    String user_id = args[1];
                    String password = args[2];
                    String point = args[3];
                    
                    fitSleep = Integer.parseInt(point);
                    // send URL
                    URL url = new URL(S_url+user_id+"/"+password+"/"+point);
                    System.out.println("url에 연결중입니다. url : " + S_url+user_id+"/"+password+"/"+point);
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
                        newiteml.add(ChatColor.GREEN + "Exp_bottle to Level up");
                        
                        ItemStack newitem = new ItemStack(Material.EXP_BOTTLE);
                        ItemMeta newitemm = newitem.getItemMeta();
                        newitemm.setDisplayName("FitSleep_EXP");
                        newitemm.setLore(newiteml);
                        newitem.setItemMeta(newitemm);
                        
                        Inventory inv = Bukkit.createInventory(null, 9 , ChatColor.LIGHT_PURPLE + "new inventory");
                        //inv.setItem(1, newitem);
                        //inv.addItem(newitem);
                        for (int reward = 0; reward < fitSleep; reward++)
                        {
                            player.getInventory().addItem(newitem);
                            inv.addItem(newitem);
                        }

                        
                        System.out.println(player.getName()+" success to get fitcoin");
                    }
                    else{
                        sender.sendMessage(">> /fitcraft sleep fityou_id fityou_password fitcoin : to get a reward");
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

        else if (args[0].equals("heart")){
            URLConnection urlConnectrion = null;
            
            // URL 주소
            if(args.length != 4){
                sender.sendMessage(">> /fitcraft heart <fityou_id> <fityou_password> <Amount>");
            }
            else{
                try{
                    player.sendMessage("Start to get Heart reward! 1 hour = 1 Heart Posion");

                    Runtime rt = Runtime.getRuntime();
                    String S_url = "http://fityou.xyz/fitapp/fitHeart/";
                    String user_id = args[1];
                    String password = args[2];
                    String point = args[3];
                    
                    fitHeart = Integer.parseInt(point);
                    // send URL
                    URL url = new URL(S_url+user_id+"/"+password+"/"+point);
                    System.out.println("url에 연결중입니다. url : " + S_url+user_id+"/"+password+"/"+point);
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
                        
                        ItemStack is = new ItemStack(Material.POTION, 1, (short) 8236);
                        PotionMeta im = (PotionMeta) is.getItemMeta();
                        im.setMainEffect(PotionEffectType.HEALTH_BOOST);
                        im.setDisplayName("FitHealth Posion");
                        im.addCustomEffect(new PotionEffect(PotionEffectType.HEALTH_BOOST, 1200* Integer.parseInt(point), 10000), true);
                        is.setItemMeta(im);
                        //player.getInventory().addItem(is);
                        
                        ////
                        player.sendMessage("Get Health Potion");

                        
                        Inventory inv = Bukkit.createInventory(null, 9 , ChatColor.LIGHT_PURPLE + "new inventory");
                        //inv.setItem(1, newitem);
                        //inv.addItem(newitem);
                        for (int reward = 0; reward < fitSleep; reward++)
                        {
                            player.getInventory().addItem(is);
                            inv.addItem(is);
                        }
                        

                        
                        System.out.println(player.getName()+" success to get Health posion");
                    }
                    else{
                        sender.sendMessage(">> /fitcraft heart fityou_id fityou_password amount : to get a reward");
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
        
        else if (args[0].equals("gamble")){      
            
            ArrayList<String> newItem = new ArrayList<>();
            newItem.add("");
            newItem.add(ChatColor.DARK_PURPLE + "FitGambleTicket");
            
            player.sendMessage("Gamble Ticket!");
            ItemStack ticket = new ItemStack(Material.PAPER);
            ItemMeta meta = ticket.getItemMeta();
            meta.setDisplayName("FitGambleTicket");
            
            meta.setLore(newItem);
            ticket.setItemMeta(meta);
            
            player.getInventory().addItem(ticket);
        }
                 
        return false;
    }
}
