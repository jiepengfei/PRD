using System;
using System.IO;
using UnityEditor;
using UnityEngine;

// Art settings only. Does not create UI, change game state, or replace existing GUIDs.
public static class BattleSettlementArtImporter
{
    [Serializable] private class Manifest { public Entry[] assets; }
    [Serializable] private class Entry
    {
        public string file;
        public float[] border;
        public float[] pivot;
        public float ppu;
        public int width;
        public int height;
    }

    [MenuItem("Tools/Wuxia/Battle Settlement/Apply Art Import Settings")]
    private static void Apply()
    {
        string file = EditorUtility.OpenFilePanel("Select settlement manifest.json", Application.dataPath, "json");
        if (string.IsNullOrEmpty(file)) return;
        string assetsRoot = Normalize(Application.dataPath) + "/";
        string root = Normalize(Path.GetDirectoryName(file)) + "/";
        if (!root.StartsWith(assetsRoot, StringComparison.OrdinalIgnoreCase))
            throw new InvalidDataException("Copy the package below project Assets first.");
        Manifest manifest = JsonUtility.FromJson<Manifest>(File.ReadAllText(file));
        if (manifest == null || manifest.assets == null)
            throw new InvalidDataException("Invalid settlement manifest.");
        AssetDatabase.Refresh();

        // Validate all entries before changing any import settings.
        foreach (Entry entry in manifest.assets)
        {
            if (entry == null || string.IsNullOrEmpty(entry.file) || entry.border == null ||
                entry.border.Length != 4 || entry.pivot == null || entry.pivot.Length != 2 ||
                entry.ppu <= 0 || entry.width <= 0 || entry.height <= 0)
                throw new InvalidDataException("Invalid sprite settings.");
            string absolute = Normalize(Path.Combine(root, entry.file));
            if (!absolute.StartsWith(root, StringComparison.OrdinalIgnoreCase) || !File.Exists(absolute))
                throw new InvalidDataException("Missing sprite or path outside package: " + entry.file);
            foreach (float border in entry.border)
                if (border < 0) throw new InvalidDataException("Negative sprite border.");
            if (entry.border[0] + entry.border[2] >= entry.width ||
                entry.border[1] + entry.border[3] >= entry.height)
                throw new InvalidDataException("Border exceeds sprite size.");
            if (!(AssetImporter.GetAtPath("Assets/" + absolute.Substring(assetsRoot.Length)) is TextureImporter))
                throw new InvalidDataException("Not an imported texture: " + entry.file);
        }

        foreach (Entry entry in manifest.assets)
        {
            string absolute = Normalize(Path.Combine(root, entry.file));
            string assetPath = "Assets/" + absolute.Substring(assetsRoot.Length);
            TextureImporter importer = (TextureImporter)AssetImporter.GetAtPath(assetPath);
            importer.textureType = TextureImporterType.Sprite;
            importer.spriteImportMode = SpriteImportMode.Single;
            importer.spritePixelsPerUnit = entry.ppu;
            importer.spriteBorder = new Vector4(entry.border[0], entry.border[1], entry.border[2], entry.border[3]);
            importer.sRGBTexture = true;
            importer.alphaSource = TextureImporterAlphaSource.FromInput;
            importer.alphaIsTransparency = true;
            importer.mipmapEnabled = false;
            importer.wrapMode = TextureWrapMode.Clamp;
            importer.filterMode = FilterMode.Bilinear;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.maxTextureSize = Mathf.Clamp(Mathf.NextPowerOfTwo(Math.Max(entry.width, entry.height)), 32, 8192);
            var settings = new TextureImporterSettings();
            importer.ReadTextureSettings(settings);
            settings.spriteAlignment = (int)SpriteAlignment.Custom;
            settings.spritePivot = new Vector2(entry.pivot[0], entry.pivot[1]);
            settings.spriteMeshType = SpriteMeshType.FullRect;
            importer.SetTextureSettings(settings);
            importer.SaveAndReimport();
        }
        Debug.Log("Battle Settlement: applied art settings to " + manifest.assets.Length + " sprites. UI assembly and business wiring remain separate.");
    }

    private static string Normalize(string path)
    {
        return Path.GetFullPath(path).Replace('\\', '/').TrimEnd('/');
    }
}
