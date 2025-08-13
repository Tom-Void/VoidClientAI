package com.example.mod.blocks;

import net.minecraft.block.Block;
import net.minecraft.block.Material;
import net.fabricmc.fabric.api.object.builder.v1.block.FabricBlockSettings;

public class ExampleBlock extends Block {
    public ExampleBlock() {
        super(FabricBlockSettings.of(Material.STONE).strength(3.0f, 3.0f));
    }
}