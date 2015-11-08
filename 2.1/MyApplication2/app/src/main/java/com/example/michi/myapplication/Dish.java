package com.example.michi.myapplication;

/**
 * Created by michi on 02.11.2015.
 * Property class to represent a dish.
 */
class Dish {
    private String category; // e.g. "Stew".
    private String menue; // e.g. "Potato soup with bacon & beef broth 2,3,A,B,A1 with poultry wiener 2,3,8,B, bread roll A,G,A1,A3"
    private String price; // e.g. "1,80€".
    private String extra; // e.g. "Parisian potatoes or rice".

    public Dish() {
        this.category = "";
        this.menue = "";
        this.price = "";
        this.extra = "";
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public void setMenue(String menue) {
        this.menue = menue;
    }

    public void setPrice(String price) {
        this.price = price;
    }

    public void setExtra(String extra) {
        this.extra = extra;
    }

    public String getCategory() {
        return this.category;
    }

    public String getMenue() {
        return this.menue;
    }

    public String getPrice() {
        return this.price;
    }

    public String getExtra() {
        return this.extra;
    }
}
